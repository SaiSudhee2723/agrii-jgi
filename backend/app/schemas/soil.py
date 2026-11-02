from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class ImageQualityMetrics(BaseModel):
    is_acceptable: bool
    blur_score: float = Field(..., description="Laplacian variance (>100 is crisp, <60 is blurry)")
    blur_status: str
    glare_ratio: float = Field(..., description="Percentage of overexposed highlight pixels (<5% recommended)")
    lighting_status: str
    width: int
    height: int
    mean_rgb: List[float]

class SoilColorAnalysis(BaseModel):
    dominant_color_hex: str
    color_description: str
    estimated_soil_texture: str
    estimated_moisture_level: str

class SoilAnalysisReport(BaseModel):
    id: Optional[str] = None
    quality_status: str  # 'passed', 'suboptimal', 'rejected'
    quality_metrics: ImageQualityMetrics
    color_analysis: SoilColorAnalysis
    nitrogen_level: str = "Laboratory Test Required"
    phosphorus_level: str = "Laboratory Test Required"
    potassium_level: str = "Laboratory Test Required"
    scientific_disclaimer: str
    lab_test_recommended: bool = True
    recommendations: List[str]
    raw_details: Dict[str, Any] = {}
    created_at: Optional[str] = None

class ManualSoilTestCreate(BaseModel):
    nitrogen: float = Field(..., ge=0, le=500, description="Nitrogen measurement in kg/ha or mg/kg")
    phosphorus: float = Field(..., ge=0, le=300, description="Phosphorus measurement in kg/ha or mg/kg")
    potassium: float = Field(..., ge=0, le=500, description="Potassium measurement in kg/ha or mg/kg")
    ph: float = Field(..., ge=0.0, le=14.0, description="Soil pH level")
    electrical_conductivity: Optional[float] = Field(None, ge=0, le=20.0, description="EC in dS/m")
    moisture: Optional[float] = Field(None, ge=0, le=100.0, description="Soil moisture percentage")
    measurement_type: str = Field("manual_entry", description="Source: 'manual_entry', 'laboratory_report', 'physical_sensor'")
    lab_name: Optional[str] = Field("Accredited Agricultural Lab", description="Testing laboratory or equipment name")
    notes: Optional[str] = None

class SoilTestRecord(BaseModel):
    id: str
    user_id: str
    measurement_type: str
    nitrogen: Optional[float] = None
    phosphorus: Optional[float] = None
    potassium: Optional[float] = None
    ph: Optional[float] = None
    electrical_conductivity: Optional[float] = None
    moisture: Optional[float] = None
    lab_name: Optional[str] = None
    soil_texture: Optional[str] = None
    condition_summary: str
    recommendations: List[str]
    created_at: str
    data_source: str


