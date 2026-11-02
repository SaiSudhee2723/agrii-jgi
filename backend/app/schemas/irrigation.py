from typing import List, Optional
from pydantic import BaseModel, Field

class IrrigationCalculationRequest(BaseModel):
    crop_name: str = Field(..., description="Target crop (e.g., 'Wheat', 'Rice', 'Maize', 'Cotton', 'Tomato')")
    growth_stage: str = Field(..., description="Growth stage: 'initial', 'vegetative', 'flowering', 'yield_formation', 'ripening'")
    soil_moisture_percentage: float = Field(..., ge=0, le=100, description="Current soil moisture percentage")
    field_area_acres: float = Field(default=1.0, gt=0, description="Field area in acres")
    temperature_celsius: Optional[float] = Field(default=28.0, description="Ambient temperature")
    humidity_percentage: Optional[float] = Field(default=55.0, description="Relative humidity")
    forecast_rainfall_mm: Optional[float] = Field(default=0.0, description="Forecast rainfall over next 24-48 hours")

class IrrigationCalculationResponse(BaseModel):
    crop_name: str
    growth_stage: str
    soil_moisture_status: str  # 'Deficit', 'Adequate', 'Saturated'
    irrigation_needed: bool
    water_required_liters_per_acre: float
    total_water_liters: float
    evapotranspiration_rate_mm_day: float
    schedule_recommendation: str
    water_saving_tips: List[str]

