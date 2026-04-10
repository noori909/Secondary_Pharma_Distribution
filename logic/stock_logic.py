from data.database import SessionLocal
from data.models import Product, StockMovement


def _apply_change(product_id, quantity_delta, reason, note=None):
    if quantity_delta == 0:
        raise ValueError("Quantity change cannot be zero")

    session = SessionLocal()
    try:
        product = session.query(Product).filter(Product.id == product_id).first()
        if not product:
            raise ValueError("Product not found")

        new_qty = product.quantity_in_stock + quantity_delta
        if new_qty < 0:
            raise ValueError(
                f"Stock would become negative (current {product.quantity_in_stock}, "
                f"change {quantity_delta:+d})"
            )

        product.quantity_in_stock = new_qty
        movement = StockMovement(
            product_id=product.id,
            quantity_delta=quantity_delta,
            reason=reason,
            note=note,
        )
        session.add(movement)
        session.commit()
        return movement.id, new_qty
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def record_purchase(product_id, quantity, note=None):
    """Increase stock (distributor purchase / inward)."""
    q = int(quantity)
    if q <= 0:
        raise ValueError("Purchase quantity must be positive")
    return _apply_change(product_id, q, "purchase", note)


def record_adjustment(product_id, quantity_delta, reason, note=None):
    """
    Signed stock correction: positive adds, negative removes.
    reason: damage | expiry | correction | other
    """
    delta = int(quantity_delta)
    allowed = {"damage", "expiry", "correction", "other"}
    if reason not in allowed:
        raise ValueError(f"reason must be one of: {', '.join(sorted(allowed))}")
    return _apply_change(product_id, delta, reason, note)


def get_recent_movements(limit=100):
    session = SessionLocal()
    try:
        rows = (
            session.query(StockMovement, Product)
            .join(Product, StockMovement.product_id == Product.id)
            .order_by(StockMovement.id.desc())
            .limit(limit)
            .all()
        )
        out = []
        for m, p in rows:
            out.append(
                {
                    "id": m.id,
                    "created_at": m.created_at,
                    "product_id": p.id,
                    "product_name": p.name,
                    "quantity_now": p.quantity_in_stock,
                    "quantity_delta": m.quantity_delta,
                    "reason": m.reason,
                    "note": m.note or "",
                }
            )
        return out
    finally:
        session.close()
