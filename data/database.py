from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = "sqlite:///pharma.db"

engine = create_engine(
    DATABASE_URL,
    echo=True  # shows SQL in terminal (learning + debugging)
)

SessionLocal = sessionmaker(bind=engine)

Base = declarative_base()
