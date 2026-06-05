"""
Sales transaction endpoints
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from config.database import get_db
from models.models import Sale, SaleItem
from schemas.schemas import SaleCreate, SaleResponse

router = APIRouter()


@router.post("", response_model=SaleResponse)
async def create_sale(sale: SaleCreate, db: Session = Depends(get_db)):
    existing = db.query(Sale).filter(Sale.invoice_number == sale.invoice_number).first()
    if existing:
        return existing

    db_sale = Sale(
        invoice_number=sale.invoice_number,
        cashier_id=sale.cashier_id,
        total_amount=sale.total_amount,
        discount=sale.discount or 0,
        net_amount=sale.net_amount,
        payment_method=sale.payment_method,
        is_voided=False,
    )
    db.add(db_sale)
    db.flush()

    for item in sale.items:
        db_item = SaleItem(
            sale_id=db_sale.id,
            product_id=item.product_id,
            barcode=item.barcode,
            product_name=item.product_name,
            quantity=item.quantity,
            cost_price_at_sale=item.cost_price_at_sale,
            retail_price_at_sale=item.retail_price_at_sale,
            subtotal=item.subtotal,
        )
        db.add(db_item)

    db.commit()
    db.refresh(db_sale)
    return db_sale


@router.get("", response_model=list[SaleResponse])
async def get_sales(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
    is_voided: Optional[bool] = None,
    db: Session = Depends(get_db),
):
    query = db.query(Sale)
    if is_voided is not None:
        query = query.filter(Sale.is_voided == is_voided)
    return query.order_by(Sale.created_at.desc()).offset(skip).limit(limit).all()
