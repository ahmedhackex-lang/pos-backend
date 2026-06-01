"""
Sales transaction endpoints
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from config.database import get_db
from models.models import Sale, SaleItem
from schemas.schemas import SaleCreate, SaleResponse

router = APIRouter()


@router.post("/", response_model=SaleResponse)
async def create_sale(sale: SaleCreate, db: Session = Depends(get_db)):
    # Check duplicate
    existing = db.query(Sale).filter(Sale.invoice_number == sale.invoice_number).first()
    if existing:
        return SaleResponse.from_orm(existing)  # Idempotent
    
    # Create sale
    db_sale = Sale(
        invoice_number=sale.invoice_number,
        cashier_id=sale.cashier_id,
        total_amount=sale.total_amount,
        discount=sale.discount,
        net_amount=sale.net_amount,
        payment_method=sale.payment_method
    )
    db.add(db_sale)
    db.flush()
    
    # Create items
    for item in sale.items:
        db_item = SaleItem(
            sale_id=db_sale.id,
            **item.dict()
        )
        db.add(db_item)
    
    db.commit()
    db.refresh(db_sale)
    return db_sale


@router.get("/", response_model=List[SaleResponse])
async def get_sales(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    sales = db.query(Sale).offset(skip).limit(limit).all()
    return sales