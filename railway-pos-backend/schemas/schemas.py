"""
Pydantic schemas for request/response validation
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from decimal import Decimal


# ===== USER SCHEMAS =====
class UserBase(BaseModel):
    username: str
    full_name: Optional[str] = None
    role: str


class UserCreate(UserBase):
    password: str


class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


# ===== PRODUCT SCHEMAS =====
class ProductBase(BaseModel):
    barcode: str
    name: str
    category: Optional[str] = None
    brand: Optional[str] = None
    cost_price: Decimal
    retail_price: Decimal
    stock_quantity: int = 0
    reorder_alert_level: int = 5


class ProductCreate(ProductBase):
    pass


class ProductResponse(ProductBase):
    id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


# ===== SALE SCHEMAS =====
class SaleItemCreate(BaseModel):
    product_id: int
    barcode: str
    product_name: str
    quantity: Decimal
    cost_price_at_sale: Decimal
    retail_price_at_sale: Decimal
    subtotal: Decimal


class SaleCreate(BaseModel):
    invoice_number: str
    cashier_id: int
    total_amount: Decimal
    discount: Decimal = 0
    net_amount: Decimal
    payment_method: str
    items: List[SaleItemCreate]


class SaleItemResponse(BaseModel):
    id: int
    product_name: str
    quantity: Decimal
    retail_price_at_sale: Decimal
    subtotal: Decimal
    
    class Config:
        from_attributes = True


class SaleResponse(BaseModel):
    id: int
    invoice_number: str
    cashier_id: int
    total_amount: Decimal
    net_amount: Decimal
    payment_method: str
    created_at: datetime
    items: List[SaleItemResponse]
    
    class Config:
        from_attributes = True


# ===== AUTH SCHEMAS =====
class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


# ===== GENERIC RESPONSE =====
class APIResponse(BaseModel):
    success: bool
    data: Optional[dict] = None
    message: Optional[str] = None
    error: Optional[dict] = None