from data.database import SessionLocal
from data.models import Customer


def add_customer(name):
    name = (name or "").strip()
    if not name:
        raise ValueError("Name is required")

    session = SessionLocal()
    try:
        customer = Customer(name=name)
        session.add(customer)
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def update_customer(customer_id, name):
    name = (name or "").strip()
    if not name:
        raise ValueError("Name is required")

    session = SessionLocal()
    try:
        customer = session.query(Customer).filter(Customer.id == customer_id).first()
        if not customer:
            raise ValueError("Customer not found")
        customer.name = name
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def set_customer_status(customer_id, status):
    session = SessionLocal()
    try:
        customer = session.query(Customer).filter(Customer.id == customer_id).first()
        if not customer:
            raise ValueError("Customer not found")
        customer.status = status
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def get_all_customers(include_inactive=True):
    session = SessionLocal()
    try:
        query = session.query(Customer)
        if not include_inactive:
            query = query.filter(Customer.status == "active")
        return query.order_by(Customer.name.asc()).all()
    finally:
        session.close()
