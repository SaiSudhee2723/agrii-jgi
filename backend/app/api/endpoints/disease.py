import json
import uuid
import logging
from datetime import datetime
from typing import Optional, Dict, Any
from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile, status
from app.core.database import get_sqlite_conn
from app.core.security import get_current_user_optional
from app.schemas.disease import DiseaseDiagnosisResponse
from app.services.disease_inference_service import DiseaseInferenceService
from app.services.npk_inference_service import NPKInferenceService

logger = logging.getLogger("geosense.api.disease")
router = APIRouter()

ALLOWED_MIME_TYPES = {"image/jpeg", "image/jpg", "image/png", "image/webp"}
MAX_FILE_SIZE = 15 * 1024 * 1024


@router.post(
    "/diagnose-disease",
    response_model=DiseaseDiagnosisResponse,
    summary="Grounded plant infection & leaf disease diagnosis (multipart upload or base64 JSON)"
)
async def diagnose_crop_disease(
    request: Request,
    file: Optional[UploadFile] = File(None, description="Leaf/crop photo uploaded or captured from camera"),
    lang: Optional[str] = Form("en"),
    question: Optional[str] = Form(None),
    crop: Optional[str] = Form(None),
    lat: Optional[float] = Form(None),
    lon: Optional[float] = Form(None),
    current_user: Optional[Dict[str, Any]] = Depends(get_current_user_optional),
):
    """
    Two-stage grounded diagnostic endpoint:
    1. Runs PlantVillage ONNX disease model (< 0.50 confidence asks for clearer close-up)
       and cross-checks against real-dataset npk_model.onnx.
    2. Correlates live local weather + ICAR/UAS Dharwad treatments in target language (en, kn, hi, mr, ta, te).
    """
    contents: Optional[bytes] = None
    eff_lang = (lang or "en").strip().lower()
    eff_question = question
    eff_crop = crop
    eff_lat = lat
    eff_lon = lon
    weather_override = None

    if file is not None:
        if file.content_type and file.content_type.lower() not in ALLOWED_MIME_TYPES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid image type '{file.content_type}'. Supported formats: JPEG, PNG, WEBP."
            )
        contents = await file.read()
    else:
        ctype = (request.headers.get("content-type") or "").lower()
        if "application/json" in ctype:
            try:
                body = await request.json()
            except Exception as exc:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid JSON payload: {exc}")
            b64_img = body.get("image_base64") or body.get("image")
            if not b64_img:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing 'image_base64' field.")
            try:
                contents = NPKInferenceService.decode_base64_image(b64_img)
            except ValueError as ve:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))

            eff_lang = (body.get("lang") or body.get("language") or eff_lang or "en").strip().lower()
            eff_question = body.get("question") or body.get("message") or eff_question
            eff_crop = body.get("crop") or eff_crop
            eff_lat = body.get("lat") if body.get("lat") is not None else eff_lat
            eff_lon = body.get("lon") if body.get("lon") is not None else eff_lon
            weather_override = body.get("weather")
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Provide either multipart 'file' upload or JSON body with 'image_base64'."
            )

    if not contents or len(contents) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="Image payload is empty or exceeds the 15 MB limit."
        )

    try:
        result = await DiseaseInferenceService.diagnose_from_bytes(
            image_bytes=contents,
            lang=eff_lang,
            question=eff_question,
            crop_hint=eff_crop,
            latitude=eff_lat,
            longitude=eff_lon,
            weather_override=weather_override,
        )
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(ve))
    except Exception as exc:
        logger.error(f"Disease diagnosis failed: {exc}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Crop disease diagnosis failed.")

    user_id = current_user.get("sub") if current_user else "anonymous"
    rec_id = str(uuid.uuid4())
    now_str = datetime.utcnow().isoformat() + "Z"
    result.id = rec_id
    result.created_at = now_str

    try:
        conn = get_sqlite_conn()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO disease_scans (
                id, user_id, condition_name, pathogen_or_cause, status_category,
                confidence, why_infected, solution_json, npk_crosscheck_json, detected_language, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                rec_id,
                user_id,
                result.condition_name,
                result.pathogen_or_cause,
                result.status_category,
                result.confidence,
                result.why_infected,
                json.dumps(result.immediate_solution.model_dump(), ensure_ascii=False),
                json.dumps(result.npk_crosscheck.model_dump(), ensure_ascii=False) if result.npk_crosscheck else None,
                result.detected_language,
                now_str,
            ),
        )
        conn.commit()
        conn.close()
    except Exception as db_exc:
        logger.warning(f"Failed to persist disease scan record cleanly: {db_exc}")

    return result

