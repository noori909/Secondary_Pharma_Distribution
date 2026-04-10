from data.database import SessionLocal
from data.models import Rep


def add_rep(name):
    name = (name or "").strip()
    if not name:
        raise ValueError("Name is required")

    session = SessionLocal()
    try:
        rep = Rep(name=name)
        session.add(rep)
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def update_rep(rep_id, name):
    name = (name or "").strip()
    if not name:
        raise ValueError("Name is required")

    session = SessionLocal()
    try:
        rep = session.query(Rep).filter(Rep.id == rep_id).first()
        if not rep:
            raise ValueError("Rep not found")
        rep.name = name
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def set_rep_status(rep_id, status):
    session = SessionLocal()
    try:
        rep = session.query(Rep).filter(Rep.id == rep_id).first()
        if not rep:
            raise ValueError("Rep not found")
        rep.status = status
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def get_all_reps(include_inactive=True):
    session = SessionLocal()
    try:
        query = session.query(Rep)
        if not include_inactive:
            query = query.filter(Rep.status == "active")
        return query.order_by(Rep.name.asc()).all()
    finally:
        session.close()

