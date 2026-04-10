from data.database import SessionLocal
from data.models import Product


def add_product(
    name,
    company,
    trade_price,
    mrp=None,
    quantity=0,
    batch=None,
    formula=None,
    description=None,
):
    if mrp is None:
        mrp = trade_price

    session = SessionLocal()
    product = Product(
        name=name,
        company=company,
        trade_price=trade_price,
        mrp=mrp,
        quantity_in_stock=quantity,
        batch=batch,
        formula=formula,
        description=description,
    )
    session.add(product)
    session.commit()
    session.close()

    
def get_product_by_id(product_id):
    session = SessionLocal()
    try:
        return session.query(Product).filter(Product.id == product_id).first()
    finally:
        session.close()


def get_all_products():
    session = SessionLocal()
    products = session.query(Product).all()
    session.close()
    return products


def update_product(
    product_id,
    name,
    company,
    trade_price,
    mrp,
    batch=None,
    formula=None,
    description=None,
):
    if mrp is None:
        mrp = trade_price

    session = SessionLocal()
    try:
        product = session.query(Product).filter(Product.id == product_id).first()
        if not product:
            raise ValueError("Product not found")

        product.name = name
        product.company = company
        product.trade_price = float(trade_price)
        product.mrp = float(mrp)
        product.batch = batch
        product.formula = formula
        product.description = description

        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def set_product_status(product_id, status):
    session = SessionLocal()
    try:
        product = session.query(Product).filter(Product.id == product_id).first()
        if not product:
            raise ValueError("Product not found")
        product.status = status
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
