"""
Dashboard analytics endpoints
- Defensive: handles empty database, missing data
- Returns clean JSON for dashboard
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from config.database import get_db
from models.models import Sale, SaleItem, Product

router = APIRouter()


@router.get("/stats")
async def get_dashboard_stats(db: Session = Depends(get_db)):
    """Get dashboard KPIs"""
    try:
        # Total revenue (sum of net_amount, excluding voided)
        total_revenue = (
            db.query(func.coalesce(func.sum(Sale.net_amount), 0))
            .filter(Sale.is_voided == False)
            .scalar()
        ) or 0

        # Total transactions
        total_transactions = (
            db.query(func.count(Sale.id))
            .filter(Sale.is_voided == False)
            .scalar()
        ) or 0

        # Average transaction
        average_transaction = (
            float(total_revenue) / total_transactions
            if total_transactions > 0
            else 0.0
        )

        # Top products (by revenue)
        top_products_raw = (
            db.query(
                SaleItem.product_name,
                func.sum(SaleItem.quantity).label("quantity_sold"),
                func.sum(SaleItem.subtotal).label("revenue"),
            )
            .join(Sale, SaleItem.sale_id == Sale.id)
            .filter(Sale.is_voided == False)
            .group_by(SaleItem.product_name)
            .order_by(func.sum(SaleItem.subtotal).desc())
            .limit(10)
            .all()
        )

        # Inventory stats
        total_products = (
            db.query(func.count(Product.id))
            .filter(Product.is_active == True)
            .scalar()
        ) or 0

        low_stock_count = (
            db.query(func.count(Product.id))
            .filter(
                Product.is_active == True,
                Product.stock_quantity <= Product.reorder_alert_level,
            )
            .scalar()
        ) or 0

        return {
            "success": True,
            "data": {
                "total_revenue": float(total_revenue),
                "total_transactions": int(total_transactions),
                "average_transaction": float(average_transaction),
                "total_products": int(total_products),
                "low_stock_count": int(low_stock_count),
                "top_products": [
                    {
                        "name": p.product_name,
                        "quantity_sold": float(p.quantity_sold or 0),
                        "revenue": float(p.revenue or 0),
                    }
                    for p in top_products_raw
                ],
            },
        }
    except Exception as e:
        return {
            "success": False,
            "error": {
                "code": "DASHBOARD_ERROR",
                "message": str(e),
            },
        }


@router.get("/sales-chart")
async def get_sales_chart(
    days: int = 7,
    db: Session = Depends(get_db),
):
    """Get daily sales for the last N days"""
    try:
        from datetime import datetime, timedelta

        start_date = datetime.utcnow() - timedelta(days=days)

        results = (
            db.query(
                func.date(Sale.created_at).label("date"),
                func.sum(Sale.net_amount).label("revenue"),
                func.count(Sale.id).label("count"),
            )
            .filter(Sale.created_at >= start_date, Sale.is_voided == False)
            .group_by(func.date(Sale.created_at))
            .order_by(func.date(Sale.created_at))
            .all()
        )

        return {
            "success": True,
            "data": [
                {
                    "date": str(r.date),
                    "revenue": float(r.revenue or 0),
                    "count": int(r.count or 0),
                }
                for r in results
            ],
        }
    except Exception as e:
        return {
            "success": False,
            "error": {"code": "CHART_ERROR", "message": str(e)},
        }
