from data.database import SessionLocal
from data.models import Customer


def add_customer(name):
    session = SessionLocal()
    customer = Customer(name=name)
    session.add(customer)
    session.commit()
    session.close()


def set_customer_status(customer_id, status):
    session = SessionLocal()
    customer = session.query(Customer).filter(Customer.id == customer_id).first()

    if not customer:
        session.close()
        raise ValueError("Customer not found")

    customer.status = status
    session.commit()
    session.close()


def get_all_customers(include_inactive=True):
    session = SessionLocal()

    query = session.query(Customer)
    if not include_inactive:
        query = query.filter(Customer.status == "active")

    customers = query.all()
    session.close()
    return customers
