import os
import logging
from typing import List, Dict, Any, Tuple
import numpy as np

logger = logging.getLogger("geosense.crop")

try:
    from sklearn.ensemble import RandomForestClassifier
    import joblib
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    logger.warning("Scikit-learn not installed; running with heuristic decision matrix fallback.")

from app.schemas.crop import (
    CropRecommendationRequest,
    CropRecommendationResponse,
    AlternativeCrop,
    GrowingConditions
)

# Reference agronomic profiles for crops
CROP_AGRONOMIC_DATA: Dict[str, Dict[str, Any]] = {
    "Rice": {
        "temp_range": "20°C - 35°C",
        "water_req": "High (1200 - 1800 mm)",
        "ph_pref": "5.5 - 7.0 (Slightly acidic to neutral)",
        "advice": [
            "Maintain 2-5 cm standing water during tillering to panicle initiation.",
            "Apply Nitrogen in 3 splits (basal, active tillering, and panicle initiation) to prevent leaching.",
            "Monitor for blast and brown plant hopper during high humidity periods."
        ]
    },
    "Maize": {
        "temp_range": "18°C - 30°C",
        "water_req": "Moderate (500 - 800 mm)",
        "ph_pref": "5.8 - 7.2 (Well-drained fertile loam)",
        "advice": [
            "Ensure field has excellent drainage; maize is sensitive to waterlogging.",
            "Side-dress urea at knee-high and tasseling stages for optimum cob filling.",
            "Maintain planting depth of 3-5 cm with 60x20 cm spacing."
        ]
    },
    "Chickpea": {
        "temp_range": "15°C - 25°C",
        "water_req": "Low (300 - 450 mm)",
        "ph_pref": "6.0 - 7.5 (Neutral to slightly alkaline)",
        "advice": [
            "Inoculate seeds with Rhizobium culture before sowing to enhance biological N-fixation.",
            "Avoid excessive nitrogen fertilization to prevent vegetative overgrowth.",
            "Provide one life-saving irrigation at pod development if winter rains fail."
        ]
    },
    "Cotton": {
        "temp_range": "21°C - 35°C",
        "water_req": "Moderate (600 - 1000 mm)",
        "ph_pref": "6.0 - 8.0 (Deep black clay loam or alluvial)",
        "advice": [
            "Ensure deep tillage to encourage deep taproot development.",
            "Apply balanced Potassium (K) to improve fiber strength and boll weight.",
            "Scout weekly for pink bollworm and sucking pests from 45 days after emergence."
        ]
    },
    "Wheat": {
        "temp_range": "12°C - 25°C",
        "water_req": "Moderate (450 - 650 mm)",
        "ph_pref": "6.0 - 7.5",
        "advice": [
            "Crown root initiation (21 days after sowing) is the most critical irrigation stage.",
            "Ensure phosphorus is placed near the seed zone at sowing.",
            "Spray micro-nutrients (Zinc sulphate) if yellowing appears in young leaves."
        ]
    },
    "Tomato": {
        "temp_range": "18°C - 28°C",
        "water_req": "Moderate (600 - 800 mm)",
        "ph_pref": "6.0 - 6.8",
        "advice": [
            "Use drip irrigation with fertigation to reduce fungal foliar diseases.",
            "Stake indeterminate varieties to keep fruit off moist soil.",
            "Apply calcium to prevent blossom end rot during high fruit load."
        ]
    },
    "Sugarcane": {
        "temp_range": "24°C - 38°C",
        "water_req": "High (1500 - 2500 mm)",
        "ph_pref": "6.5 - 7.5",
        "advice": [
            "Trash mulching in inter-rows reduces soil moisture loss by 30%.",
            "Apply nitrogen in splits up to 90 days after planting.",
            "Earthing-up at 90-120 days prevents lodging during monsoon winds."
        ]
    },
    "Banana": {
        "temp_range": "22°C - 35°C",
        "water_req": "High (1800 - 2200 mm)",
        "ph_pref": "6.0 - 7.5",
        "advice": [
            "Requires abundant potassium for bunch development and fruit size.",
            "Desuckering is vital to channel nutrition to the mother plant.",
            "Mulch with dry banana leaves to retain root moisture."
        ]
    }
}

class CropRecommendationService:
    """Module 2: Crop recommendation engine using Scikit-Learn Random Forest."""

    _model: Any = None
    _classes: List[str] = list(CROP_AGRONOMIC_DATA.keys())

    @classmethod
    def _initialize_model(cls):
        """Builds and trains a baseline calibrated Random Forest classifier on standard agronomic data."""
        if not SKLEARN_AVAILABLE:
            return

        # Synthetic multi-point agricultural dataset representing diverse climatic & nutrient envelopes
        # Features: [N, P, K, temp, humidity, pH, rainfall]
        data = [
            # Rice (High N, Moderate P, K, warm, high humidity, high rainfall)
            [80, 40, 40, 26, 82, 6.5, 1200], [90, 45, 42, 28, 85, 6.2, 1400], [75, 38, 35, 25, 80, 6.0, 1100],
            # Maize (Balanced NPK, moderate rainfall, warm)
            [70, 45, 40, 24, 65, 6.5, 650], [80, 50, 45, 26, 68, 6.8, 720], [65, 40, 38, 22, 60, 6.2, 580],
            # Chickpea (Low N, moderate P, K, cool, low rainfall)
            [25, 60, 45, 18, 45, 7.2, 350], [20, 55, 40, 17, 40, 7.0, 320], [30, 65, 50, 20, 50, 7.4, 400],
            # Cotton (Moderate N, high K, warm, moderate humidity & rain)
            [75, 40, 70, 28, 60, 7.2, 750], [85, 45, 75, 30, 65, 7.5, 800], [70, 35, 65, 27, 58, 7.0, 700],
            # Wheat (Moderate N, P, cool temperature, moderate humidity)
            [80, 50, 40, 16, 55, 6.8, 500], [90, 55, 45, 18, 60, 7.0, 550], [75, 45, 38, 15, 50, 6.5, 480],
            # Tomato (High P, K, warm, moderate humidity)
            [60, 70, 75, 23, 62, 6.4, 600], [65, 75, 80, 25, 65, 6.6, 650], [55, 65, 70, 22, 58, 6.2, 550],
            # Sugarcane (High N, warm, high water)
            [120, 60, 80, 30, 78, 7.0, 1600], [130, 65, 85, 32, 80, 7.2, 1800], [110, 55, 75, 29, 75, 6.8, 1500],
            # Banana (High K, high N, warm, humid)
            [100, 70, 110, 27, 82, 6.5, 1900], [110, 75, 120, 29, 85, 6.8, 2000], [95, 65, 105, 26, 80, 6.4, 1800]
        ]
        labels = [
            "Rice", "Rice", "Rice",
            "Maize", "Maize", "Maize",
            "Chickpea", "Chickpea", "Chickpea",
            "Cotton", "Cotton", "Cotton",
            "Wheat", "Wheat", "Wheat",
            "Tomato", "Tomato", "Tomato",
            "Sugarcane", "Sugarcane", "Sugarcane",
            "Banana", "Banana", "Banana"
        ]

        clf = RandomForestClassifier(n_estimators=30, random_state=42, max_depth=6)
        clf.fit(data, labels)
        cls._model = clf
        cls._classes = list(clf.classes_)
        logger.info("Crop recommendation Random Forest model trained and initialized successfully.")

    @classmethod
    def recommend(cls, req: CropRecommendationRequest) -> CropRecommendationResponse:
        if cls._model is None:
            cls._initialize_model()

        input_vector = [
            req.nitrogen,
            req.phosphorus,
            req.potassium,
            req.temperature,
            req.humidity,
            req.ph,
            req.rainfall
        ]

        if cls._model is not None:
            probas = cls._model.predict_proba([input_vector])[0]
            sorted_indices = np.argsort(probas)[::-1]

            primary_crop = cls._classes[sorted_indices[0]]
            primary_conf = float(round(probas[sorted_indices[0]], 3))

            alternatives: List[AlternativeCrop] = []
            for idx in sorted_indices[1:4]:
                conf = float(round(probas[idx], 3))
                crop_name = cls._classes[idx]
                suitability = "High" if conf > 0.25 else ("Moderate" if conf > 0.10 else "Marginal")
                alternatives.append(AlternativeCrop(
                    crop=crop_name,
                    confidence=conf,
                    suitability=suitability
                ))
        else:
            # Fallback heuristic calculation
            primary_crop, primary_conf, alternatives = cls._heuristic_recommend(req)

        crop_info = CROP_AGRONOMIC_DATA.get(primary_crop, {
            "temp_range": "20°C - 30°C",
            "water_req": "Moderate",
            "ph_pref": "6.0 - 7.5",
            "advice": ["Follow regional agricultural extension package of practices."]
        })

        return CropRecommendationResponse(
            primary_crop=primary_crop,
            confidence_score=primary_conf,
            alternative_crops=alternatives,
            growing_conditions=GrowingConditions(
                ideal_temp_range=crop_info["temp_range"],
                water_requirement=crop_info["water_req"],
                soil_ph_preference=crop_info["ph_pref"]
            ),
            farming_recommendations=crop_info["advice"],
            input_summary={
                "N": req.nitrogen,
                "P": req.phosphorus,
                "K": req.potassium,
                "temperature": req.temperature,
                "humidity": req.humidity,
                "pH": req.ph,
                "rainfall": req.rainfall
            }
        )

    @classmethod
    def _heuristic_recommend(cls, req: CropRecommendationRequest) -> Tuple[str, float, List[AlternativeCrop]]:
        # Heuristic scoring when sklearn is unavailable
        if req.rainfall > 1000 and req.temperature > 24:
            return "Rice", 0.78, [
                AlternativeCrop(crop="Banana", confidence=0.15, suitability="Moderate"),
                AlternativeCrop(crop="Sugarcane", confidence=0.07, suitability="Marginal")
            ]
        elif req.temperature < 20 and req.rainfall < 600:
            return "Wheat", 0.82, [
                AlternativeCrop(crop="Chickpea", confidence=0.12, suitability="Moderate"),
                AlternativeCrop(crop="Maize", confidence=0.06, suitability="Marginal")
            ]
        elif req.nitrogen < 40 and req.rainfall < 500:
            return "Chickpea", 0.75, [
                AlternativeCrop(crop="Wheat", confidence=0.18, suitability="Moderate"),
                AlternativeCrop(crop="Cotton", confidence=0.07, suitability="Marginal")
            ]
        else:
            return "Maize", 0.70, [
                AlternativeCrop(crop="Tomato", confidence=0.20, suitability="Moderate"),
                AlternativeCrop(crop="Cotton", confidence=0.10, suitability="Marginal")
            ]

