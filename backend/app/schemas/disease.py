from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class DiseaseTopPrediction(BaseModel):
    label: str
    confidence: float


class NPKCrossCheckInfo(BaseModel):
    nitrogen: float
    phosphorus: float
    potassium: float
    status: Dict[str, str]
    deficiency_suspected: bool = False
    note: str = ""


class DiseaseSolutionPlan(BaseModel):
    immediate_field_action: List[str] = []
    organic_cultural: List[str] = []
    chemical_targeted: List[str] = []
    spray_notes: str = ""


class DiseaseDiagnosisResponse(BaseModel):
    id: Optional[str] = None
    disease_name: str = ""
    condition_name: str
    pathogen_type: str = ""
    pathogen_or_cause: str
    observed_symptoms: str = ""
    status_category: str = Field(..., description="Infected | Healthy | Deficiency | Unclear")
    confidence: float
    low_confidence: bool = False
    why_infected: str
    immediate_solution: DiseaseSolutionPlan
    solution_to_fix: Optional[DiseaseSolutionPlan] = None
    prevention: List[str] = []
    lesion_metrics: Dict[str, float] = {}
    npk_crosscheck: Optional[NPKCrossCheckInfo] = None
    weather_context: Dict[str, Any] = {}
    farm_context_chips: List[str] = []
    top_predictions: List[DiseaseTopPrediction] = []
    detected_language: str = "en"
    language_name: str = "English"
    model_source: str = "OpenCV Lesion Vision + PlantVillage ONNX + ICAR Grounding"
    inference_engine: str = "Hybrid Vision + ICAR Pathology"
    scientific_disclaimer: str
    created_at: Optional[str] = None
