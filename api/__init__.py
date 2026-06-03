"""
API router aggregation
Exports all route modules for the Grocery POS Backend
"""

from .auth import router as auth_router
from .products import router as products_router
from .sales import router as sales_router
from .dashboard import router as dashboard_router

__all__ = [
    'auth_router',
    'products_router',
    'sales_router',
    'dashboard_router'
]
