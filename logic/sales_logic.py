from data.database import SessionLocal
from data.models import Sale, SaleItem, Product, Rep, Area, Customer
from datetime import date


def record_bill(rep_id, area_id, items, sale_date=None, customer_id=None):
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
            date=sale_date
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
    )


def get_all_sales():
    session = SessionLocal()
    sales = session.query(Sale).all()
    session.close()
    return sales

def get_sales_by_rep(rep_id):
    session = SessionLocal()
    sales = session.query(Sale).filter(Sale.rep_id == rep_id).all()
    session.close()
    return sales

def get_sales_by_area(area_id):
    session = SessionLocal()
    sales = session.query(Sale).filter(Sale.area_id == area_id).all()
    session.close()
    return sales

def get_sales_by_product(product_id):
    session = SessionLocal()
    sales = session.query(Sale).filter(Sale.product_id == product_id).all()
    session.close()
    return sales
