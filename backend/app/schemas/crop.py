from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class CropRecommendationRequest(BaseModel):
    nitrogen: float = Field(..., ge=0, le=300, description="Soil Nitrogen content (N) in kg/ha or mg/kg")
    phosphorus: float = Field(..., ge=0, le=300, description="Soil Phosphorus content (P) in kg/ha or mg/kg")
    potassium: float = Field(..., ge=0, le=300, description="Soil Potassium content (K) in kg/ha or mg/kg")
    temperature: float = Field(..., ge=-10, le=60, description="Ambient temperature in Celsius")
    humidity: float = Field(..., ge=0, le=100, description="Relative humidity in percentage")
    ph: float = Field(..., ge=0, le=14, description="Soil pH level")
    rainfall: float = Field(..., ge=0, le=2000, description="Average annual/seasonal rainfall in mm")

class AlternativeCrop(BaseModel):
    crop: str
    confidence: float
    suitability: str  # 'High', 'Moderate', 'Marginal'

class GrowingConditions(BaseModel):
    ideal_temp_range: str
    water_requirement: str
    soil_ph_preference: str

class CropRecommendationResponse(BaseModel):
    primary_crop: str
    confidence_score: float
    alternative_crops: List[AlternativeCrop]
    growing_conditions: GrowingConditions
    farming_recommendations: List[str]
    input_summary: Dict[str, float]

