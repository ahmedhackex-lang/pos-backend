"""
Product management endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from config.database import get_db
from models.models import Product
from schemas.schemas import ProductCreate, ProductResponse

router = APIRouter()


@router.get("", response_model=list[ProductResponse])
async def get_products(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    search: Optional[str] = None,
    is_active: Optional[bool] = True,
    db: Session = Depends(get_db),
):
    """List products with optional search"""
    query = db.query(Product)
    if is_active is not None:
        query = query.filter(Product.is_active == is_active)
    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            (Product.name.ilike(search_filter))
            | (Product.barcode.ilike(search_filter))
            | (Product.category.ilike(search_filter))
        )
    products = query.order_by(Product.name).offset(skip).limit(limit).all()
    return products


@router.get("/{barcode}", response_model=ProductResponse)
async def get_product_by_barcode(barcode: str, db: Session = Depends(get_db)):
    """Get a product by its barcode"""
    product = db.query(Product).filter(Product.barcode == barcode).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.post("", response_model=ProductResponse)
async def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    """Create a new product"""
    # Check for duplicate barcode
    existing = (
        db.query(Product).filter(Product.barcode == product.barcode).first()
    )
    if existing:
        raise HTTPException(
            status_code=409,
            detail=f"Product with barcode {product.barcode} already exists",
        )
    db_product = Product(**product.dict())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product


@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: int,
    product_update: ProductCreate,
    db: Session = Depends(get_db),
):
    """Update a product"""
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    for key, value in product_update.dict().items():
        setattr(db_product, key, value)
    db.commit()
    db.refresh(db_product)
    return db_product


@router.delete("/{product_id}")
async def delete_product(product_id: int, db: Session = Depends(get_db)):
    """Soft-delete a product (sets is_active=False)"""
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    db_product.is_active = False
    db.commit()
    return {"success": True, "message": "Product deactivated"}
