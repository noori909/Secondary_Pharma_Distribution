from data.database import SessionLocal
from data.models import Product


def add_product(name, company, trade_price):
    session = SessionLocal()
    product = Product(
        name=name,
        company=company,
        trade_price=trade_price
    )
    session.add(product)
    session.commit()
    session.close()
    
def get_all_products():
    session = SessionLocal()
    products = session.query(Product).all()
    session.close()
    return products
