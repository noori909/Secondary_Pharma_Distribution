from data.database import SessionLocal
from data.models import Area

def add_area(name):
    session = SessionLocal()
    area = Area(name=name)
    session.add(area)
    session.commit()
    session.close()

def set_area_status(area_id, status):
    session = SessionLocal()
    area = session.query(Area).filter(Area.id == area_id).first()

    if not area:
        session.close()
        raise ValueError("Area not found")

    area.status = status
    session.commit()
    session.close()

def get_all_areas(include_inactive=True):
    session = SessionLocal()

    query = session.query(Area)
    if not include_inactive:
        query = query.filter(Area.status == "active")

    areas = query.all()
    session.close()
    return areas
