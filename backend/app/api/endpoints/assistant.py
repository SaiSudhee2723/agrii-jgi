import logging
from typing import Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from app.services.assistant_service import AssistantService
from app.core.security import get_current_user_optional

logger = logging.getLogger("geosense.api.assistant")
router = APIRouter()

class ChatQueryRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=1200, description="Farmer agronomy question")
    language: Optional[str] = Field("en", description="Farmer selected language code ('en', 'hi', 'kn', 'mr', 'ta', 'te')")
    language_name: Optional[str] = Field(None, description="Full human-readable target language name")
    lat: Optional[float] = Field(None, ge=-90.0, le=90.0, description="Optional live farm latitude")
    lon: Optional[float] = Field(None, ge=-180.0, le=180.0, description="Optional live farm longitude")
    diagnosis_context: Optional[Dict[str, Any]] = Field(None, description="Optional active visual disease scan context for follow-ups")


@router.post("/chat", summary="Consult the AI Agronomy Assistant with genuine farm context")
async def chat_with_assistant(
    payload: ChatQueryRequest,
    current_user: Optional[Dict[str, Any]] = Depends(get_current_user_optional)
):
    """
    Module 8: AI Agriculture Assistant.
    Generates agronomic responses grounded in:
    - Authenticated farmer profile & region
    - Saved soil test records (sanitized for nulls)
    - Live OpenWeatherMap / Open-Meteo weather telemetry
    - Strict native-script multilingual adherence & script auto-detection
    """
    user_id = current_user.get("sub") if current_user else "anonymous"
    user_profile = current_user.get("user_metadata") if current_user else None

    try:
        response = await AssistantService.generate_response(
            question=payload.message,
            user_id=user_id,
            user_profile=user_profile,
            language=payload.language or "en",
            language_name=payload.language_name,
            latitude=payload.lat,
            longitude=payload.lon,
            diagnosis_context=payload.diagnosis_context,
        )
        return response
    except Exception as e:
        logger.error(f"Assistant error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error processing agronomic inquiry."
        )

