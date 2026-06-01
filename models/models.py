"""
SQLAlchemy models for PostgreSQL
"""
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, Numeric
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from config.database import Base


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(100))
    role = Column(String(20), nullable=False, index=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_login = Column(DateTime(timezone=True))
    
    sales = relationship("Sale", back_populates="cashier", foreign_keys="Sale.cashier_id")


class Product(Base):
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    barcode = Column(String(100), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False, index=True)
    category = Column(String(100), index=True)
    brand = Column(String(100))
    cost_price = Column(Numeric(10, 2), nullable=False, default=0)
    retail_price = Column(Numeric(10, 2), nullable=False)
    stock_quantity = Column(Integer, default=0)
    reorder_alert_level = Column(Integer, default=5)
    is_active = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class Sale(Base):
    __tablename__ = "sales"
    
    id = Column(Integer, primary_key=True, index=True)
    invoice_number = Column(String(100), unique=True, nullable=False, index=True)
    cashier_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    total_amount = Column(Numeric(10, 2), nullable=False)
    discount = Column(Numeric(10, 2), default=0)
    net_amount = Column(Numeric(10, 2), nullable=False)
    payment_method = Column(String(30), nullable=False)
    is_voided = Column(Boolean, default=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    cashier = relationship("User", back_populates="sales", foreign_keys=[cashier_id])
    items = relationship("SaleItem", back_populates="sale", cascade="all, delete-orphan")


class SaleItem(Base):
    __tablename__ = "sale_items"
    
    id = Column(Integer, primary_key=True, index=True)
    sale_id = Column(Integer, ForeignKey("sales.id", ondelete="CASCADE"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    barcode = Column(String(100), nullable=False)
    product_name = Column(String(255), nullable=False)
    quantity = Column(Numeric(10, 3), nullable=False)
    cost_price_at_sale = Column(Numeric(10, 2), nullable=False)
    retail_price_at_sale = Column(Numeric(10, 2), nullable=False)
    subtotal = Column(Numeric(10, 2), nullable=False)
    
    sale = relationship("Sale", back_populates="items")