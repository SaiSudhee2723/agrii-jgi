import logging
from typing import List, Optional
from fastapi import APIRouter, Query
from app.schemas.market import MarketPriceRecord, CommodityAnalysis
from app.services.market_service import MarketService

logger = logging.getLogger("geosense.api.market")
router = APIRouter()

@router.get("/prices", response_model=List[MarketPriceRecord], summary="List agricultural commodity mandi prices")
async def list_market_prices(
    commodity: Optional[str] = Query(None, description="Filter by crop/commodity name"),
    state: Optional[str] = Query(None, description="Filter by Indian State"),
    mandi: Optional[str] = Query(None, description="Filter by Mandi market name")
):
    """
    Module 5: Mandi Price Explorer.
    Returns modal, min, and max market rates with clear 'demo' vs 'live' status labeling.
    """
    return MarketService.get_prices(commodity=commodity, state=state, mandi_name=mandi)

@router.get("/analysis", response_model=CommodityAnalysis, summary="Get weekly commodity price trend & analysis")
async def get_commodity_trends(
    commodity: str = Query("Wheat", description="Commodity name for trend visualization")
):
    """Returns 7-day price trajectory, weekly percentage change, and Mandi comparison."""
    return MarketService.get_commodity_analysis(commodity=commodity)

