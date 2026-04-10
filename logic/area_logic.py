from data.database import SessionLocal
from data.models import Area


def add_area(name):
    name = (name or "").strip()
    if not name:
        raise ValueError("Name is required")

    session = SessionLocal()
    try:
        area = Area(name=name)
        session.add(area)
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def update_area(area_id, name):
    name = (name or "").strip()
    if not name:
        raise ValueError("Name is required")

    session = SessionLocal()
    try:
        area = session.query(Area).filter(Area.id == area_id).first()
        if not area:
            raise ValueError("Area not found")
        area.name = name
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def set_area_status(area_id, status):
    session = SessionLocal()
    try:
        area = session.query(Area).filter(Area.id == area_id).first()
        if not area:
            raise ValueError("Area not found")
        area.status = status
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def get_all_areas(include_inactive=True):
    session = SessionLocal()
    try:
        query = session.query(Area)
        if not include_inactive:
            query = query.filter(Area.status == "active")
        return query.order_by(Area.name.asc()).all()
    finally:
        session.close()
