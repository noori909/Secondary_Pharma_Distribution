"""
Filtered sales reporting and aggregates for export.
Rows are built from sale line items (SaleItem); legacy bills without lines use Sale header.
"""
from collections import defaultdict
from datetime import date

from sqlalchemy import exists, func

from data.database import SessionLocal
from data.models import Sale, SaleItem, Product, Rep, Area, Customer, StockMovement


def _parse_date_optional(value):
    if value is None:
        return None
    if isinstance(value, date):
        return value
    s = str(value).strip()
    if not s:
        return None
    parts = s.replace("/", "-").split("-")
    if len(parts) == 3:
        y, m, d = int(parts[0]), int(parts[1]), int(parts[2])
        return date(y, m, d)
    raise ValueError(f"Invalid date: {value!r} (use YYYY-MM-DD)")


def get_report_detail_rows(
    date_from=None,
    date_to=None,
    rep_id=None,
    area_id=None,
    product_id=None,
    customer_id=None,
):
    """
    Line-level rows matching filters. Each dict is one exported row / tree row.
    """
    date_from = _parse_date_optional(date_from)
    date_to = _parse_date_optional(date_to)

    session = SessionLocal()
    try:
        rows = []

        def sale_filters():
            fs = []
            if date_from is not None:
                fs.append(Sale.date >= date_from)
            if date_to is not None:
                fs.append(Sale.date <= date_to)
            if rep_id is not None:
                fs.append(Sale.rep_id == rep_id)
            if area_id is not None:
                fs.append(Sale.area_id == area_id)
            if customer_id is not None:
                fs.append(Sale.customer_id == customer_id)
            return fs

        # Line items (normal bills)
        q = (
            session.query(SaleItem, Sale, Product, Rep, Area, Customer)
            .select_from(SaleItem)
            .join(Sale, SaleItem.sale_id == Sale.id)
            .join(Product, SaleItem.product_id == Product.id)
            .join(Rep, Sale.rep_id == Rep.id)
            .join(Area, Sale.area_id == Area.id)
            .outerjoin(Customer, Sale.customer_id == Customer.id)
        )
        for f in sale_filters():
            q = q.filter(f)
        if product_id is not None:
            q = q.filter(SaleItem.product_id == product_id)

        for si, sale, prod, rep, area, cust in q.order_by(
            Sale.date, Sale.id, SaleItem.id
        ).all():
            cid = cust.id if cust else None
            cname = cust.name if cust else ""
            rows.append(
                {
                    "sale_id": sale.id,
                    "sale_date": sale.date,
                    "rep_id": rep.id,
                    "rep_name": rep.name,
                    "area_id": area.id,
                    "area_name": area.name,
                    "customer_id": cid,
                    "customer_name": cname or "—",
                    "product_id": prod.id,
                    "product_name": prod.name,
                    "company": prod.company,
                    "batch": prod.batch or "",
                    "mrp": si.mrp,
                    "trade_price": si.trade_price,
                    "quantity": si.quantity,
                    "line_discount": si.discount,
                    "line_net": si.line_total,
                    "sale_total_qty": sale.quantity,
                    "sale_total_discount": sale.discount,
                    "sale_net_amount": sale.net_amount,
                }
            )

        # Legacy: sale with no sale_items
        has_items = exists().where(SaleItem.sale_id == Sale.id)
        q2 = (
            session.query(Sale, Product, Rep, Area, Customer)
            .select_from(Sale)
            .join(Product, Sale.product_id == Product.id)
            .join(Rep, Sale.rep_id == Rep.id)
            .join(Area, Sale.area_id == Area.id)
            .outerjoin(Customer, Sale.customer_id == Customer.id)
            .filter(~has_items)
        )
        for f in sale_filters():
            q2 = q2.filter(f)
        if product_id is not None:
            q2 = q2.filter(Sale.product_id == product_id)

        for sale, prod, rep, area, cust in q2.order_by(Sale.date, Sale.id).all():
            cid = cust.id if cust else None
            cname = cust.name if cust else ""
            qty = sale.quantity
            line_net = sale.net_amount
            rows.append(
                {
                    "sale_id": sale.id,
                    "sale_date": sale.date,
                    "rep_id": rep.id,
                    "rep_name": rep.name,
                    "area_id": area.id,
                    "area_name": area.name,
                    "customer_id": cid,
                    "customer_name": cname or "—",
                    "product_id": prod.id,
                    "product_name": prod.name,
                    "company": prod.company,
                    "batch": prod.batch or "",
                    "mrp": prod.mrp,
                    "trade_price": prod.trade_price,
                    "quantity": qty,
                    "line_discount": sale.discount,
                    "line_net": line_net,
                    "sale_total_qty": sale.quantity,
                    "sale_total_discount": sale.discount,
                    "sale_net_amount": sale.net_amount,
                }
            )

        rows.sort(key=lambda r: (r["sale_date"], r["sale_id"], r["product_id"]))
        return rows
    finally:
        session.close()


def summarize_totals(detail_rows):
    """Grand totals from line-level rows."""
    bills = {r["sale_id"] for r in detail_rows}
    return {
        "bill_count": len(bills),
        "line_count": len(detail_rows),
        "quantity": sum(r["quantity"] for r in detail_rows),
        "line_discount": sum(r["line_discount"] for r in detail_rows),
        "net_sales": sum(r["line_net"] for r in detail_rows),
        "benefit_8pct": sum(r["line_net"] for r in detail_rows) * 0.08,
    }


def aggregate_by_rep(detail_rows):
    agg = defaultdict(lambda: {"qty": 0, "line_discount": 0.0, "net": 0.0, "bills": set()})
    for r in detail_rows:
        k = (r["rep_id"], r["rep_name"])
        agg[k]["qty"] += r["quantity"]
        agg[k]["line_discount"] += r["line_discount"]
        agg[k]["net"] += r["line_net"]
        agg[k]["bills"].add(r["sale_id"])
    out = []
    for (rid, rname), v in sorted(agg.items(), key=lambda x: x[0][1].lower()):
        net = v["net"]
        out.append(
            {
                "rep_id": rid,
                "rep_name": rname,
                "bills": len(v["bills"]),
                "quantity": v["qty"],
                "line_discount": v["line_discount"],
                "net_sales": net,
                "benefit_8pct": net * 0.08,
            }
        )
    return out


def aggregate_by_area(detail_rows):
    agg = defaultdict(lambda: {"qty": 0, "line_discount": 0.0, "net": 0.0, "bills": set()})
    for r in detail_rows:
        k = (r["area_id"], r["area_name"])
        agg[k]["qty"] += r["quantity"]
        agg[k]["line_discount"] += r["line_discount"]
        agg[k]["net"] += r["line_net"]
        agg[k]["bills"].add(r["sale_id"])
    out = []
    for (aid, aname), v in sorted(agg.items(), key=lambda x: x[0][1].lower()):
        net = v["net"]
        out.append(
            {
                "area_id": aid,
                "area_name": aname,
                "bills": len(v["bills"]),
                "quantity": v["qty"],
                "line_discount": v["line_discount"],
                "net_sales": net,
                "benefit_8pct": net * 0.08,
            }
        )
    return out


def aggregate_by_product(detail_rows):
    agg = defaultdict(
        lambda: {"qty": 0, "line_discount": 0.0, "net": 0.0, "bills": set()}
    )
    for r in detail_rows:
        k = (r["product_id"], r["product_name"], r.get("company") or "")
        agg[k]["qty"] += r["quantity"]
        agg[k]["line_discount"] += r["line_discount"]
        agg[k]["net"] += r["line_net"]
        agg[k]["bills"].add(r["sale_id"])
    out = []
    for (pid, pname, company), v in sorted(agg.items(), key=lambda x: x[0][1].lower()):
        net = v["net"]
        out.append(
            {
                "product_id": pid,
                "product_name": pname,
                "company": company,
                "bills": len(v["bills"]),
                "quantity": v["qty"],
                "line_discount": v["line_discount"],
                "net_sales": net,
                "benefit_8pct": net * 0.08,
            }
        )
    return out


def aggregate_by_customer(detail_rows):
    agg = defaultdict(
        lambda: {"qty": 0, "line_discount": 0.0, "net": 0.0, "bills": set()}
    )
    for r in detail_rows:
        cid = r["customer_id"]
        cname = r["customer_name"] or "—"
        k = (cid if cid is not None else -1, cname)
        agg[k]["qty"] += r["quantity"]
        agg[k]["line_discount"] += r["line_discount"]
        agg[k]["net"] += r["line_net"]
        agg[k]["bills"].add(r["sale_id"])
    out = []
    for (cid, cname), v in sorted(
        agg.items(), key=lambda x: (x[0][0] == -1, x[0][1].lower())
    ):
        net = v["net"]
        out.append(
            {
                "customer_id": None if cid == -1 else cid,
                "customer_name": cname,
                "bills": len(v["bills"]),
                "quantity": v["qty"],
                "line_discount": v["line_discount"],
                "net_sales": net,
                "benefit_8pct": net * 0.08,
            }
        )
    return out


def get_stock_movement_report_rows(
    date_from=None,
    date_to=None,
    product_id=None,
    reason=None,
):
    """
    Stock audit rows (purchase / adjustments). Filters use movement date (calendar day).
    reason: None for all, or one of purchase|damage|expiry|correction|other
    """
    date_from = _parse_date_optional(date_from)
    date_to = _parse_date_optional(date_to)

    session = SessionLocal()
    try:
        q = session.query(StockMovement, Product).join(
            Product, StockMovement.product_id == Product.id
        )
        if date_from is not None:
            q = q.filter(func.date(StockMovement.created_at) >= date_from)
        if date_to is not None:
            q = q.filter(func.date(StockMovement.created_at) <= date_to)
        if product_id is not None:
            q = q.filter(StockMovement.product_id == product_id)
        if reason:
            q = q.filter(StockMovement.reason == reason)

        rows = []
        for m, p in q.order_by(StockMovement.id.desc()).all():
            rows.append(
                {
                    "movement_id": m.id,
                    "created_at": m.created_at,
                    "product_id": p.id,
                    "product_name": p.name,
                    "company": p.company,
                    "quantity_delta": m.quantity_delta,
                    "reason": m.reason,
                    "note": m.note or "",
                }
            )
        return rows
    finally:
        session.close()


def summarize_stock_movements(stock_rows):
    """Totals for stock movement list."""
    qty_in = sum(r["quantity_delta"] for r in stock_rows if r["quantity_delta"] > 0)
    qty_out = sum(r["quantity_delta"] for r in stock_rows if r["quantity_delta"] < 0)
    net = qty_in + qty_out
    return {
        "movement_count": len(stock_rows),
        "qty_in": qty_in,
        "qty_out": abs(qty_out),
        "net_delta": net,
    }
