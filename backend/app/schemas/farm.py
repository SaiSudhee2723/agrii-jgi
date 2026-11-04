from typing import List, Optional, Any
from pydantic import BaseModel, Field

class FarmCreate(BaseModel):
    farm_name: str = Field(..., min_length=1, max_length=120, description="Name or identifier of the farm / plot")
    latitude: float = Field(..., ge=-90.0, le=90.0, description="Center latitude of the farm")
    longitude: float = Field(..., ge=-180.0, le=180.0, description="Center longitude of the farm")
    boundary_coordinates: Optional[List[List[float]]] = Field(default=[], description="Polygon boundary as [[lat, lon], ...]")
    area_acres: Optional[float] = Field(default=0.0, ge=0.0, description="Approximate calculated farm size in acres")
    crop_type: Optional[str] = Field(default="General Crop", max_length=100, description="Primary crop cultivated")

class FarmUpdate(BaseModel):
    farm_name: Optional[str] = Field(None, min_length=1, max_length=120)
    latitude: Optional[float] = Field(None, ge=-90.0, le=90.0)
    longitude: Optional[float] = Field(None, ge=-180.0, le=180.0)
    boundary_coordinates: Optional[List[List[float]]] = None
    area_acres: Optional[float] = Field(None, ge=0.0)
    crop_type: Optional[str] = Field(None, max_length=100)

class FarmResponse(BaseModel):
    id: str
    user_id: str
    farm_name: str
    latitude: float
    longitude: float
    boundary_coordinates: Optional[List[List[float]]] = []
    area_acres: float = 0.0
    crop_type: Optional[str] = "General Crop"
    created_at: str
    updated_at: str
