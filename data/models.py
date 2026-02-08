

from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Date,
    ForeignKey
)
from sqlalchemy.orm import relationship
from data.database import Base

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    company = Column(String, nullable=False)
    trade_price = Column(Float, nullable=False)
    status = Column(String, default="active")

    sales = relationship("Sale", back_populates="product")


class Rep(Base):
    __tablename__ = "reps"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    status = Column(String, default="active")

    sales = relationship("Sale", back_populates="rep")
    bonuses = relationship("Bonus", back_populates="rep")

class Area(Base):
    __tablename__ = "areas"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    status = Column(String, default="active")

    sales = relationship("Sale", back_populates="area")

class Sale(Base):
    __tablename__ = "sales"

    id = Column(Integer, primary_key=True)
    date = Column(Date, nullable=False)

    rep_id = Column(Integer, ForeignKey("reps.id"), nullable=False)
    area_id = Column(Integer, ForeignKey("areas.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)

    quantity = Column(Integer, nullable=False)
    net_amount = Column(Float, nullable=False)

    rep = relationship("Rep", back_populates="sales")
    area = relationship("Area", back_populates="sales")
    product = relationship("Product", back_populates="sales")

class Bonus(Base):
    __tablename__ = "bonuses"

    id = Column(Integer, primary_key=True)
    rep_id = Column(Integer, ForeignKey("reps.id"), nullable=False)
    period = Column(String, nullable=False)  # e.g. "2026-02"
    bonus_amount = Column(Float, nullable=False)

    rep = relationship("Rep", back_populates="bonuses")

