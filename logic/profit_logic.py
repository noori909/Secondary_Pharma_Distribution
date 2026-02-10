
from data.database import SessionLocal
from data.models import Sale

def calculate_total_profit():
    """
    Calculates 8% of all net sales.
    """
    session = SessionLocal()
    total_net = session.query(Sale).with_entities(Sale.net_amount).all()
    session.close()

    # total_net is list of tuples
    total = sum([x[0] for x in total_net])
    profit = total * 0.08
    return profit

def calculate_profit_by_rep(rep_id):
    """
    Calculates 8% of net sales for a given rep.
    """
    session = SessionLocal()
    sales = session.query(Sale.net_amount).filter(Sale.rep_id == rep_id).all()
    session.close()

    total = sum([x[0] for x in sales])
    profit = total * 0.08
    return profit

def calculate_profit_by_area(area_id):
    """
    Calculates 8% of net sales for a given area.
    """
    session = SessionLocal()
    sales = session.query(Sale.net_amount).filter(Sale.area_id == area_id).all()
    session.close()

    total = sum([x[0] for x in sales])
    profit = total * 0.08
    return profit

