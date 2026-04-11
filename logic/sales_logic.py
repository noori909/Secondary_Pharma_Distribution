from datetime import date

from sqlalchemy import and_, or_, exists
from sqlalchemy.orm import joinedload

from data.database import SessionLocal
from data.models import Sale, SaleItem, Product, Rep, Area, Customer

def record_bill(rep_id, area_id, items, sale_date=None, customer_id=None, payment_status="cash"):
    """
    Records a single bill with one Sale header and multiple SaleItem rows.
    items: list[{"product_id": int, "quantity": int, "discount": float}]
    """
    if not items:
        raise ValueError("Bill must contain at least one item")

    session = SessionLocal()
    try:
        if sale_date is None:
            sale_date = date.today()

        rep = session.query(Rep).filter(
            Rep.id == rep_id,
            Rep.status == "active"
        ).first()
        if not rep:
            raise ValueError("Rep not found or inactive")

        area = session.query(Area).filter(
            Area.id == area_id,
            Area.status == "active"
        ).first()
        if not area:
            raise ValueError("Area not found or inactive")

        customer = None
        if customer_id is not None:
            customer = session.query(Customer).filter(
                Customer.id == customer_id,
                Customer.status == "active"
            ).first()
            if not customer:
                raise ValueError("Customer not found or inactive")

        total_qty = 0
        total_discount = 0.0
        total_net = 0.0
        normalized_items = []

        for item in items:
            product_id = int(item["product_id"])
            quantity = int(item["quantity"])
            discount = float(item.get("discount", 0))

            if quantity <= 0:
                raise ValueError("Quantity must be positive")
            if discount < 0:
                raise ValueError("Discount cannot be negative")

            product = session.query(Product).filter(
                Product.id == product_id,
                Product.status == "active"
            ).first()
            if not product:
                raise ValueError(f"Product {product_id} not found or inactive")
            if product.quantity_in_stock < quantity:
                raise ValueError(f"Not enough stock for {product.name}")

            base_amount = product.trade_price * quantity
            line_total = base_amount - discount
            if line_total <= 0:
                raise ValueError(f"Invalid discount for {product.name}")

            product.quantity_in_stock -= quantity

            normalized_items.append({
                "product": product,
                "quantity": quantity,
                "discount": discount,
                "line_total": line_total,
            })
            total_qty += quantity
            total_discount += discount
            total_net += line_total

        sale = Sale(
            rep_id=rep.id,
            area_id=area.id,
            customer_id=customer.id if customer else None,
            # Keep backward compatibility for old list views.
            product_id=normalized_items[0]["product"].id,
            quantity=total_qty,
            discount=total_discount,
            net_amount=total_net,
            date=sale_date,
            payment_status=payment_status
        )
        session.add(sale)
        session.flush()

        for item in normalized_items:
            product = item["product"]
            sale_item = SaleItem(
                sale_id=sale.id,
                product_id=product.id,
                quantity=item["quantity"],
                trade_price=product.trade_price,
                mrp=product.mrp,
                discount=item["discount"],
                line_total=item["line_total"],
            )
            session.add(sale_item)

        session.commit()
        return sale.id
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def record_sale(
    rep_id,
    area_id,
    product_id,
    quantity,
    discount=0,
    sale_date=None,
    customer_id=None,
    payment_status="cash",
):
    """
    Records a sale with automatic price calculation.
    """
    return record_bill(
        rep_id=rep_id,
        area_id=area_id,
        customer_id=customer_id,
        sale_date=sale_date,
        items=[
            {
                "product_id": product_id,
                "quantity": quantity,
                "discount": discount,
            }
        ],
        payment_status=payment_status,
    )


def get_sale_by_id(sale_id):
    """
    Load one sale with rep, area, customer, and line items (with product batch/name).
    Returns a dict suitable for receipt rendering, or None if not found.
    """
    session = SessionLocal()
    try:
        sale = session.query(Sale).filter(Sale.id == sale_id).first()
        if not sale:
            return None

        customer_name = None
        if sale.customer_id and sale.customer:
            customer_name = sale.customer.name

        lines = []
        for item in sale.items:
            product = item.product
            qty = item.quantity
            unit_net = item.line_total / qty if qty else 0.0
            lines.append({
                "product_name": product.name if product else f"Product #{item.product_id}",
                "batch": (product.batch or "-") if product else "-",
                "mrp": item.mrp,
                "trade_price": item.trade_price,
                "quantity": qty,
                "discount": item.discount,
                "unit_net": unit_net,
                "line_total": item.line_total,
            })

        if not lines and sale.product and sale.quantity:
            product = sale.product
            qty = sale.quantity
            unit_net = sale.net_amount / qty if qty else 0.0
            lines.append({
                "product_name": product.name,
                "batch": product.batch or "-",
                "mrp": product.mrp,
                "trade_price": product.trade_price,
                "quantity": qty,
                "discount": sale.discount,
                "unit_net": unit_net,
                "line_total": sale.net_amount,
            })

        return {
            "sale_id": sale.id,
            "date": sale.date,
            "rep_name": sale.rep.name if sale.rep else "",
            "area_name": sale.area.name if sale.area else "",
            "customer_name": customer_name,
            "payment_status": getattr(sale, 'payment_status', 'cash'),
            "total_qty": sale.quantity,
            "total_discount": sale.discount,
            "net_amount": sale.net_amount,
            "lines": lines,
        }
    finally:
        session.close()


def get_all_sales():
    """All bills, newest first (stable for UI slices and scripts)."""
    session = SessionLocal()
    try:
        return (
            session.query(Sale)
            .order_by(Sale.date.desc(), Sale.id.desc())
            .all()
        )
    finally:
        session.close()


def get_recent_sales_for_ui(limit=25):
    """
    Recent bills as plain dicts (safe after session closes).
    Includes rep / area / customer display names.
    """
    session = SessionLocal()
    try:
        rows = (
            session.query(Sale)
            .options(
                joinedload(Sale.rep),
                joinedload(Sale.area),
                joinedload(Sale.customer),
            )
            .order_by(Sale.date.desc(), Sale.id.desc())
            .limit(limit)
            .all()
        )
        return [
            {
                "id": s.id,
                "date": s.date,
                "rep_name": s.rep.name if s.rep else "",
                "area_name": s.area.name if s.area else "",
                "customer_name": s.customer.name if s.customer else "—",
                "quantity": s.quantity,
                "net_amount": s.net_amount,
            }
            for s in rows
        ]
    finally:
        session.close()


def get_sales_by_rep(rep_id):
    session = SessionLocal()
    try:
        return (
            session.query(Sale)
            .filter(Sale.rep_id == rep_id)
            .order_by(Sale.date.desc(), Sale.id.desc())
            .all()
        )
    finally:
        session.close()


def get_sales_by_area(area_id):
    session = SessionLocal()
    try:
        return (
            session.query(Sale)
            .filter(Sale.area_id == area_id)
            .order_by(Sale.date.desc(), Sale.id.desc())
            .all()
        )
    finally:
        session.close()


def get_sales_by_product(product_id):
    """
    Bills that include this product on any line (SaleItem), or legacy header-only
    rows where the sale has no line items but Sale.product_id matches.
    """
    session = SessionLocal()
    try:
        line_sale_ids = session.query(SaleItem.sale_id).filter(
            SaleItem.product_id == product_id
        )
        has_items = exists().where(SaleItem.sale_id == Sale.id)
        return (
            session.query(Sale)
            .filter(
                or_(
                    Sale.id.in_(line_sale_ids),
                    and_(Sale.product_id == product_id, ~has_items),
                )
            )
            .order_by(Sale.date.desc(), Sale.id.desc())
            .all()
        )
    finally:
        session.close()

def get_pending_credit_bills():
    session = SessionLocal()
    try:
        sales = session.query(Sale).options(
            joinedload(Sale.rep),
            joinedload(Sale.customer)
        ).filter(Sale.payment_status == 'credit').order_by(Sale.id.desc()).all()
        result = []
        for s in sales:
            result.append({
                "id": s.id,
                "date": str(s.date),
                "rep": s.rep.name if s.rep else "",
                "customer": s.customer.name if s.customer else "",
                "net_amount": s.net_amount
            })
        return result
    finally:
        session.close()

def mark_sale_paid(sale_id):
    session = SessionLocal()
    try:
        sale = session.query(Sale).filter(Sale.id == sale_id).first()
        if sale:
            sale.payment_status = "cash"
            session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
