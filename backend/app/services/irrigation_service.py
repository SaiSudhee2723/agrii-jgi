import logging
from typing import Dict, List, Tuple
from app.schemas.irrigation import IrrigationCalculationRequest, IrrigationCalculationResponse

logger = logging.getLogger("geosense.irrigation")

# FAO Crop Coefficients (Kc) across growth stages
CROP_KC_TABLE: Dict[str, Dict[str, float]] = {
    "Wheat": {"initial": 0.35, "vegetative": 0.75, "flowering": 1.15, "yield_formation": 1.05, "ripening": 0.45},
    "Rice": {"initial": 1.05, "vegetative": 1.15, "flowering": 1.25, "yield_formation": 1.10, "ripening": 0.90},
    "Maize": {"initial": 0.40, "vegetative": 0.80, "flowering": 1.20, "yield_formation": 1.05, "ripening": 0.60},
    "Cotton": {"initial": 0.45, "vegetative": 0.75, "flowering": 1.20, "yield_formation": 0.95, "ripening": 0.65},
    "Tomato": {"initial": 0.60, "vegetative": 0.85, "flowering": 1.15, "yield_formation": 0.95, "ripening": 0.70},
    "Sugarcane": {"initial": 0.40, "vegetative": 1.00, "flowering": 1.25, "yield_formation": 1.15, "ripening": 0.75},
    "Default": {"initial": 0.45, "vegetative": 0.80, "flowering": 1.15, "yield_formation": 1.00, "ripening": 0.65}
}

class IrrigationService:
    """Module 3: Software-based smart irrigation decision engine."""

    LITERS_PER_MM_PER_ACRE = 4046.86  # 1 mm of water depth over 1 acre = 4,046.86 liters

    @classmethod
    def calculate_irrigation(cls, req: IrrigationCalculationRequest) -> IrrigationCalculationResponse:
        crop_kc_map = CROP_KC_TABLE.get(req.crop_name, CROP_KC_TABLE["Default"])
        stage = req.growth_stage.lower()
        kc = crop_kc_map.get(stage, 0.85)

        # Estimate Reference Evapotranspiration ET0 (mm/day) via temperature & humidity
        temp = req.temperature_celsius if req.temperature_celsius is not None else 28.0
        rh = req.humidity_percentage if req.humidity_percentage is not None else 55.0
        rain_fc = req.forecast_rainfall_mm if req.forecast_rainfall_mm is not None else 0.0

        # Simplified Hargreaves/FAO daily ET0 approximation
        et0 = max(2.0, (0.0023 * (temp + 17.8) * 12.0) * (1.0 - (rh / 200.0)))
        etc_mm_day = round(et0 * kc, 2)

        # Soil moisture target threshold (typically 65% field capacity for top 30cm)
        field_capacity = 70.0
        wilting_threshold = 35.0
        current_sm = req.soil_moisture_percentage

        # Evaluate condition
        if current_sm >= field_capacity:
            moisture_status = "Saturated / Field Capacity"
            irrigation_needed = False
            water_depth_needed_mm = 0.0
        elif current_sm > wilting_threshold:
            deficit_pct = field_capacity - current_sm
            # Equivalent depth of water deficit
            water_depth_needed_mm = (deficit_pct / 100.0) * 35.0  # Assumes 35mm active root-zone storage
            irrigation_needed = True
            moisture_status = "Deficit"
        else:
            moisture_status = "Critical Moisture Stress"
            water_depth_needed_mm = 25.0
            irrigation_needed = True

        # Subtract effective forecast rainfall (>5mm contributes to soil reserve)
        effective_rain = max(0.0, rain_fc - 5.0)
        net_depth_mm = max(0.0, water_depth_needed_mm - effective_rain)

        if rain_fc >= 15.0:
            irrigation_needed = False
            schedule_recommendation = (
                f"Hold irrigation: {rain_fc} mm rainfall forecast over the next 24-48 hours. "
                "Natural precipitation will adequately replenish soil root zone."
            )
        elif not irrigation_needed:
            schedule_recommendation = "Soil moisture is currently optimal. No irrigation required today."
        else:
            schedule_recommendation = (
                f"Apply {round(net_depth_mm, 1)} mm of water ({round(net_depth_mm * cls.LITERS_PER_MM_PER_ACRE, 0):,.0f} L/acre). "
                "Best scheduled during early morning (5:00 AM - 8:30 AM) or evening (after 5:30 PM) to minimize evaporation losses."
            )

        water_liters_per_acre = round(net_depth_mm * cls.LITERS_PER_MM_PER_ACRE, 2)
        total_water_liters = round(water_liters_per_acre * req.field_area_acres, 2)

        tips = [
            "Adopt drip irrigation or micro-sprinklers to save up to 40-50% water compared to surface flooding.",
            "Apply 5-7 cm organic crop residue mulch around the plant base to restrict soil surface evaporation.",
            "Avoid irrigating during peak afternoon heat (12:00 PM - 3:30 PM) when atmospheric evapotranspiration is highest.",
            "Regularly inspect pipeline joints and emitters for clogs or leaks to maintain uniform water distribution."
        ]

        return IrrigationCalculationResponse(
            crop_name=req.crop_name,
            growth_stage=req.growth_stage,
            soil_moisture_status=moisture_status,
            irrigation_needed=irrigation_needed,
            water_required_liters_per_acre=water_liters_per_acre,
            total_water_liters=total_water_liters,
            evapotranspiration_rate_mm_day=etc_mm_day,
            schedule_recommendation=schedule_recommendation,
            water_saving_tips=tips
        )

