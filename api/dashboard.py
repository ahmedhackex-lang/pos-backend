"""
Dashboard analytics endpoints
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from config.database import get_db
from models.models import Sale, SaleItem, Product

router = APIRouter()


@router.get("/stats")
async def get_dashboard_stats(db: Session = Depends(get_db)):
    # Total revenue
    total_revenue = db.query(func.sum(Sale.net_amount)).filter(Sale.is_voided == False).scalar() or 0
    
    # Total transactions
    total_transactions = db.query(func.count(Sale.id)).filter(Sale.is_voided == False).scalar() or 0
    
    # Top products
    top_products = db.query(
        SaleItem.product_name,
        func.sum(SaleItem.quantity).label("quantity_sold"),
        func.sum(SaleItem.subtotal).label("revenue")
    ).join(Sale).filter(Sale.is_voided == False)\
     .group_by(SaleItem.product_name)\
     .order_by(func.sum(SaleItem.subtotal).desc())\
     .limit(10).all()
    
    return {
        "total_revenue": float(total_revenue),
        "total_transactions": total_transactions,
        "average_transaction": float(total_revenue / total_transactions) if total_transactions > 0 else 0,
        "top_products": [
            {
                "name": p.product_name,
                "quantity_sold": float(p.quantity_sold),
                "revenue": float(p.revenue)
            }
            for p in top_products
        ]
    }