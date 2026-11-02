from typing import List, Optional
from pydantic import BaseModel, Field

class MarketPriceRecord(BaseModel):
    id: Optional[str] = None
    commodity: str
    variety: str = "Common"
    mandi_name: str
    district: str
    state: str
    min_price: float
    max_price: float
    modal_price: float
    unit: str = "INR / Quintal"
    price_date: str
    is_live: bool = False
    source: str = "Agricultural Produce Market Committee"

class PriceTrendPoint(BaseModel):
    date: str
    modal_price: float

class CommodityAnalysis(BaseModel):
    commodity: str
    current_modal_price: float
    weekly_change_pct: float
    trend_direction: str  # 'up', 'down', 'stable'
    records: List[MarketPriceRecord]
    price_history: List[PriceTrendPoint]
    is_live: bool

