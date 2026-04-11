from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import sys
import os

# Ensuring config import paths resolve correctly regardless of execution angle
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import APP_DATA_DIR

db_file = APP_DATA_DIR / "pharma.db"
DATABASE_URL = f"sqlite:///{db_file.as_posix()}"

engine = create_engine(
    DATABASE_URL,
    echo=True  # shows SQL in terminal (learning + debugging)
)

SessionLocal = sessionmaker(bind=engine)

Base = declarative_base()
