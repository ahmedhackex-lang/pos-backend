"""
Dashboard analytics endpoints
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from config.database import get_db
from models.models import Sale, SaleItem, Product

router = APIRouter()


@router.get("/stats")
async def get_dashboard_stats(db: Session = Depends(get_db)):
    try:
        total_revenue = (
            db.query(func.coalesce(func.sum(Sale.net_amount), 0))
            .filter(Sale.is_voided == False).scalar()
        ) or 0

        total_transactions = (
            db.query(func.count(Sale.id))
            .filter(Sale.is_voided == False).scalar()
        ) or 0

        avg = float(total_revenue) / total_transactions if total_transactions > 0 else 0.0

        top_raw = (
            db.query(
                SaleItem.product_name,
                func.sum(SaleItem.quantity).label("qty"),
                func.sum(SaleItem.subtotal).label("rev"),
            )
            .join(Sale, SaleItem.sale_id == Sale.id)
            .filter(Sale.is_voided == False)
            .group_by(SaleItem.product_name)
            .order_by(func.sum(SaleItem.subtotal).desc())
            .limit(10).all()
        )

        total_products = (
            db.query(func.count(Product.id))
            .filter(Product.is_active == True).scalar()
        ) or 0

        low_stock = (
            db.query(func.count(Product.id))
            .filter(Product.is_active == True,
                    Product.stock_quantity <= Product.reorder_alert_level).scalar()
        ) or 0

        return {
            "success": True,
            "data": {
                "total_revenue": float(total_revenue),
                "total_transactions": int(total_transactions),
                "average_transaction": float(avg),
                "total_products": int(total_products),
                "low_stock_count": int(low_stock),
                "top_products": [
                    {"name": p.product_name,
                     "quantity_sold": float(p.qty or 0),
                     "revenue": float(p.rev or 0)}
                    for p in top_raw
                ],
            },
        }
    except Exception as e:
        return {"success": False, "error": {"code": "DASHBOARD_ERROR", "message": str(e)}}


@router.get("/sales-chart")
async def get_sales_chart(days: int = 7, db: Session = Depends(get_db)):
    try:
        start = datetime.utcnow() - timedelta(days=days)
        rows = (
            db.query(
                func.date(Sale.created_at).label("d"),
                func.sum(Sale.net_amount).label("rev"),
                func.count(Sale.id).label("cnt"),
            )
            .filter(Sale.created_at >= start, Sale.is_voided == False)
            .group_by(func.date(Sale.created_at))
            .order_by(func.date(Sale.created_at)).all()
        )
        return {
            "success": True,
            "data": [
                {"date": str(r.d), "revenue": float(r.rev or 0), "count": int(r.cnt or 0)}
                for r in rows
            ],
        }
    except Exception as e:
        return {"success": False, "error": {"code": "CHART_ERROR", "message": str(e)}}
