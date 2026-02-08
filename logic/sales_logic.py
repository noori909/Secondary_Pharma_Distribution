from data.database import SessionLocal
from data.models import Sale, Product, Rep, Area
from datetime import date

def record_sale(rep_id, area_id, product_id, quantity, net_amount, sale_date=None):
    """
    Records a sale after validating inputs.
    """
    session = SessionLocal()

    # Use today if no date provided
    if sale_date is None:
        sale_date = date.today()

    # Fetch entities
    rep = session.query(Rep).filter(Rep.id == rep_id, Rep.status == "active").first()
    area = session.query(Area).filter(Area.id == area_id, Area.status == "active").first()
    product = session.query(Product).filter(Product.id == product_id, Product.status == "active").first()

    if not rep:
        session.close()
        raise ValueError("Rep not found or inactive")
    if not area:
        session.close()
        raise ValueError("Area not found or inactive")
    if not product:
        session.close()
        raise ValueError("Product not found or inactive")
    if quantity <= 0:
        session.close()
        raise ValueError("Quantity must be positive")
    if net_amount <= 0:
        session.close()
        raise ValueError("Net amount must be positive")

    # Record sale
    sale = Sale(
        rep_id=rep.id,
        area_id=area.id,
        product_id=product.id,
        quantity=quantity,
        net_amount=net_amount,
        date=sale_date
    )

    session.add(sale)
    session.commit()
    session.close()

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
