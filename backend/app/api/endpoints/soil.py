import logging
import uuid
import json
from datetime import datetime
from typing import Optional, Dict, Any, List
from fastapi import APIRouter, UploadFile, File, HTTPException, status, Depends
from app.schemas.soil import (
    SoilAnalysisReport,
    ManualSoilTestCreate,
    SoilTestRecord
)
from app.services.soil_service import SoilAnalysisService
from app.core.security import get_current_user_optional, get_current_user_required
from app.core.supabase import get_supabase_client
from app.core.database import get_sqlite_conn

logger = logging.getLogger("geosense.api.soil")
router = APIRouter()

ALLOWED_MIME_TYPES = {"image/jpeg", "image/png", "image/webp", "image/jpg"}
MAX_FILE_SIZE = 15 * 1024 * 1024  # 15 MB

@router.post("/analyze", response_model=SoilAnalysisReport, summary="Analyze soil image for physical attributes & quality checks")
async def analyze_soil_image(
    file: UploadFile = File(..., description="Soil image captured from mobile camera or gallery upload"),
    current_user: Optional[Dict[str, Any]] = Depends(get_current_user_optional)
):
    """
    Module 1: Optical Soil Image Quality & Physical Evaluation.
    Standard RGB cameras cannot directly read chemical NPK.
    Measures observable physical metrics (texture, hue, moisture state, sharpness, lighting).
    """
    if file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid image type '{file.content_type}'. Supported formats: JPEG, PNG, WEBP."
        )

    try:
        contents = await file.read()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to read image stream: {str(e)}"
        )

    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="Image size exceeds the 15 MB limit."
        )

    try:
        report = SoilAnalysisService.evaluate_image_bytes(contents)
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(ve))
    except Exception as e:
        logger.error(f"Soil analysis failed unexpectedly: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Soil analysis processing error.")

    user_id = current_user.get("sub") if current_user else "anonymous"
    now_str = datetime.utcnow().isoformat() + "Z"
    rec_id = str(uuid.uuid4())
    report.id = rec_id
    report.created_at = now_str

    # Persist analysis to database
    try:
        conn = get_sqlite_conn()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO soil_analysis (
                id, user_id, quality_status, quality_details, color_metrics,
                soil_texture_estimate, soil_condition, measurement_type,
                scientific_disclaimer, lab_test_recommended, recommendations, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            rec_id, user_id, report.quality_status,
            json.dumps(report.quality_metrics.model_dump()),
            json.dumps(report.color_analysis.model_dump()),
            report.color_analysis.estimated_soil_texture,
            report.color_analysis.color_description,
            "optical_camera",
            report.scientific_disclaimer,
            1 if report.lab_test_recommended else 0,
            json.dumps(report.recommendations),
            now_str
        ))
        conn.commit()
        conn.close()
    except Exception as e:
        logger.warning(f"Could not save soil image analysis to local database: {e}")

    # Also persist to Supabase if available
    supabase = get_supabase_client()
    if supabase and user_id != "anonymous":
        try:
            supabase.table("soil_analysis").insert({
                "id": rec_id,
                "user_id": user_id,
                "quality_status": report.quality_status,
                "quality_details": report.quality_metrics.model_dump(),
                "color_metrics": report.color_analysis.model_dump(),
                "soil_texture_estimate": report.color_analysis.estimated_soil_texture,
                "soil_condition": report.color_analysis.color_description,
                "scientific_disclaimer": report.scientific_disclaimer,
                "lab_test_recommended": report.lab_test_recommended,
                "recommendations": report.recommendations
            }).execute()
        except Exception as e:
            logger.warning(f"Could not persist soil analysis to Supabase: {e}")

    return report

@router.post("/manual", response_model=SoilTestRecord, summary="Save actual soil laboratory or physical sensor test")
async def save_manual_soil_test(
    test_in: ManualSoilTestCreate,
    current_user: Optional[Dict[str, Any]] = Depends(get_current_user_optional)
):
    """
    Module 1: Real Soil NPK & Chemical Lab Test Ingestion.
    Accepts verified lab assay measurements (Nitrogen, Phosphorus, Potassium, pH, EC, Moisture)
    with laboratory certification attribution and saves to database.
    """
    user_id = current_user.get("sub") if current_user else "anonymous"
    now_str = datetime.utcnow().isoformat() + "Z"
    rec_id = str(uuid.uuid4())

    # Build agronomic recommendations based on real lab measurements
    recs = []
    if test_in.ph < 6.0:
        recs.append("Soil is acidic (pH < 6.0). Consider applying agricultural lime (calcium carbonate) to buffer acidity.")
    elif test_in.ph > 7.8:
        recs.append("Soil is alkaline (pH > 7.8). Apply gypsum or elemental sulfur to facilitate micronutrient uptake.")

    if test_in.nitrogen < 50:
        recs.append("Low nitrogen detected. Incorporate organic green manure, well-decomposed FYM, or split urea application.")
    elif test_in.nitrogen > 150:
        recs.append("Nitrogen level is high. Restrict synthetic N fertilizers to prevent vegetative lodging and leaching.")

    if test_in.phosphorus < 20:
        recs.append("Phosphorus is deficient (<20 kg/ha). Apply single superphosphate (SSP) or DAP placed in the root zone.")

    if test_in.potassium < 50:
        recs.append("Potassium is low. Apply Muriate of Potash (MOP) to improve plant vigor, disease resistance, and grain filling.")

    if not recs:
        recs.append("Soil nutrient balance is within normal agronomic ranges. Maintain standard maintenance fertility.")

    summary = f"Lab Verified Assay: N={test_in.nitrogen} kg/ha, P={test_in.phosphorus} kg/ha, K={test_in.potassium} kg/ha, pH={test_in.ph}"
    data_source_label = f"Certified Laboratory ({test_in.lab_name})" if test_in.measurement_type == "laboratory_report" else (
        "Physical Soil Sensor Kit" if test_in.measurement_type == "physical_sensor" else "Farmer Manual Measurement Entry"
    )

    try:
        conn = get_sqlite_conn()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO soil_analysis (
                id, user_id, quality_status, quality_details, color_metrics,
                soil_texture_estimate, soil_condition, nitrogen_ppm, phosphorus_ppm, potassium_ppm,
                soil_ph, electrical_conductivity, moisture_pct, measurement_type, lab_name,
                scientific_disclaimer, lab_test_recommended, recommendations, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            rec_id, user_id, "passed", "{}", "{}",
            "Verified by Lab Analysis", summary,
            test_in.nitrogen, test_in.phosphorus, test_in.potassium,
            test_in.ph, test_in.electrical_conductivity or 0.0, test_in.moisture or 0.0,
            test_in.measurement_type, test_in.lab_name or "Local Agricultural Lab",
            "Actual laboratory assay entry verified by farmer input.", 0,
            json.dumps(recs), now_str
        ))
        conn.commit()
        conn.close()
    except Exception as e:
        logger.error(f"Failed to persist soil test to local db: {e}")

    # Also persist to Supabase if connected
    supabase = get_supabase_client()
    if supabase and user_id != "anonymous":
        try:
            supabase.table("soil_analysis").insert({
                "id": rec_id,
                "user_id": user_id,
                "quality_status": "passed",
                "soil_condition": summary,
                "nitrogen_level": f"{test_in.nitrogen} kg/ha",
                "phosphorus_level": f"{test_in.phosphorus} kg/ha",
                "potassium_level": f"{test_in.potassium} kg/ha",
                "recommendations": recs
            }).execute()
        except Exception as e:
            logger.warning(f"Could not persist manual soil test to Supabase: {e}")

    return SoilTestRecord(
        id=rec_id,
        user_id=user_id,
        measurement_type=test_in.measurement_type,
        nitrogen=test_in.nitrogen,
        phosphorus=test_in.phosphorus,
        potassium=test_in.potassium,
        ph=test_in.ph,
        electrical_conductivity=test_in.electrical_conductivity,
        moisture=test_in.moisture,
        lab_name=test_in.lab_name,
        soil_texture="Lab Verified",
        condition_summary=summary,
        recommendations=recs,
        created_at=now_str,
        data_source=data_source_label
    )

@router.get("/history", response_model=List[SoilTestRecord], summary="Get genuine soil test records for the authenticated user")
async def get_soil_test_history(
    current_user: Optional[Dict[str, Any]] = Depends(get_current_user_optional)
):
    """
    Returns authentic soil test history for the signed-in farmer.
    Returns an empty list if no soil tests have been submitted.
    """
    user_id = current_user.get("sub") if current_user else "anonymous"

    conn = get_sqlite_conn()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM soil_analysis
        WHERE user_id = ? OR user_id = 'anonymous'
        ORDER BY created_at DESC LIMIT 20
    """, (user_id,))
    rows = cursor.fetchall()
    conn.close()

    results = []
    for r in rows:
        m_type = r["measurement_type"] or "optical_camera"
        data_source = (
            f"Laboratory Assay ({r['lab_name']})" if m_type == "laboratory_report" else (
                "Physical Field Sensor" if m_type == "physical_sensor" else (
                    "Manual Farmer Entry" if m_type == "manual_entry" else "Camera Physical Image Scan"
                )
            )
        )
        try:
            recs = json.loads(r["recommendations"]) if r["recommendations"] else []
        except Exception:
            recs = []

        results.append(SoilTestRecord(
            id=r["id"],
            user_id=r["user_id"],
            measurement_type=m_type,
            nitrogen=r["nitrogen_ppm"],
            phosphorus=r["phosphorus_ppm"],
            potassium=r["potassium_ppm"],
            ph=r["soil_ph"],
            electrical_conductivity=r["electrical_conductivity"],
            moisture=r["moisture_pct"],
            lab_name=r["lab_name"],
            soil_texture=r["soil_texture_estimate"] or "Standard Field Soil",
            condition_summary=r["soil_condition"],
            recommendations=recs,
            created_at=r["created_at"],
            data_source=data_source
        ))

    return results
