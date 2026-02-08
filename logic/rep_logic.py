from data.database import SessionLocal
from data.models import Rep

def add_rep(name):
    session = SessionLocal()
    rep = Rep(name=name)
    session.add(rep)
    session.commit()
    session.close()

def set_rep_status(rep_id, status):
    session = SessionLocal()
    rep = session.query(Rep).filter(Rep.id == rep_id).first()

    if not rep:
        session.close()
        raise ValueError("Rep not found")

    rep.status = status
    session.commit()
    session.close()

def get_all_reps(include_inactive=True):
    session = SessionLocal()

    query = session.query(Rep)
    if not include_inactive:
        query = query.filter(Rep.status == "active")

    reps = query.all()
    session.close()
    return reps

