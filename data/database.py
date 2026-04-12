from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from config import APP_DATA_DIR

db_file = APP_DATA_DIR / "pharma.db"
DATABASE_URL = f"sqlite:///{db_file.as_posix()}"

engine = create_engine(
    DATABASE_URL,
    echo=False  # Set True temporarily for SQL debugging only
)

SessionLocal = sessionmaker(bind=engine)

Base = declarative_base()
