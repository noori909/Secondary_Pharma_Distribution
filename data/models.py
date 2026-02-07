from sqlalchemy import Column, Integer, String, Float
from data.database import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    company = Column(String, nullable=False)
    trade_price = Column(Float, nullable=False)
    status = Column(String, default="active")
