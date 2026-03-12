"""Analytics routes."""

from .analytics import router as analytics_router
from .metrics import router as metrics_router

__all__ = ["analytics_router", "metrics_router"]