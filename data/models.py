from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Date,
    DateTime,
    ForeignKey,
    func,
)
from sqlalchemy.orm import relationship
from data.database import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True)

    name = Column(String, nullable=False)
    company = Column(String, nullable=False)

    trade_price = Column(Float, nullable=False)   # Distributor price
    mrp = Column(Float, nullable=False)           # Retail price

    quantity_in_stock = Column(Integer, default=0)
    batch = Column(String, nullable=True)
    formula = Column(String, nullable=True)
    description = Column(String, nullable=True)

    status = Column(String, default="active")

    sales = relationship("Sale", back_populates="product")
    sale_items = relationship("SaleItem", back_populates="product")
    stock_movements = relationship("StockMovement", back_populates="product")


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


class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    status = Column(String, default="active")

    sales = relationship("Sale", back_populates="customer")


class Sale(Base):
    __tablename__ = "sales"

    id = Column(Integer, primary_key=True)
    date = Column(Date, nullable=False)

    rep_id = Column(Integer, ForeignKey("reps.id"), nullable=False)
    area_id = Column(Integer, ForeignKey("areas.id"), nullable=False)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)

    quantity = Column(Integer, nullable=False)
    discount = Column(Float, default=0.0)
    net_amount = Column(Float, nullable=False)

    rep = relationship("Rep", back_populates="sales")
    area = relationship("Area", back_populates="sales")
    customer = relationship("Customer", back_populates="sales")
    product = relationship("Product", back_populates="sales")
    items = relationship("SaleItem", back_populates="sale", cascade="all, delete-orphan")


class SaleItem(Base):
    __tablename__ = "sale_items"

    id = Column(Integer, primary_key=True)
    sale_id = Column(Integer, ForeignKey("sales.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    trade_price = Column(Float, nullable=False)
    mrp = Column(Float, nullable=False)
    discount = Column(Float, default=0.0)
    line_total = Column(Float, nullable=False)

    sale = relationship("Sale", back_populates="items")
    product = relationship("Product", back_populates="sale_items")


class Bonus(Base):
    __tablename__ = "bonuses"

    id = Column(Integer, primary_key=True)
    rep_id = Column(Integer, ForeignKey("reps.id"), nullable=False)
    period = Column(String, nullable=False)  # e.g. "2026-02"
    bonus_amount = Column(Float, nullable=False)

    rep = relationship("Rep", back_populates="bonuses")


class StockMovement(Base):
    """Audit of non-sale stock changes (purchase, damage, expiry, manual correction)."""

    __tablename__ = "stock_movements"

    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity_delta = Column(Integer, nullable=False)
    reason = Column(String, nullable=False)
    note = Column(String, nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    product = relationship("Product", back_populates="stock_movements")

