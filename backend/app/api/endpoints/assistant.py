import logging
from typing import Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from app.services.assistant_service import AssistantService
from app.core.security import get_current_user_optional

logger = logging.getLogger("geosense.api.assistant")
router = APIRouter()

class ChatQueryRequest(BaseModel):
    message: str = Field(..., min_length=2, max_length=1000, description="Farmer agronomy question")
    language: Optional[str] = Field("en", description="Farmer selected language code ('en', 'hi', 'kn')")

@router.post("/chat", summary="Consult the AI Agronomy Assistant with genuine farm context")
async def chat_with_assistant(
    payload: ChatQueryRequest,
    current_user: Optional[Dict[str, Any]] = Depends(get_current_user_optional)
):
    """
    Module 8: AI Agriculture Assistant.
    Generates agronomic responses grounded in:
    - Authenticated farmer profile & region
    - Saved soil test records
    - Live Open-Meteo weather telemetry
    - Validated agronomic management practices
    """
    user_id = current_user.get("sub") if current_user else "anonymous"
    user_profile = current_user.get("user_metadata") if current_user else None

    try:
        response = await AssistantService.generate_response(
            question=payload.message,
            user_id=user_id,
            user_profile=user_profile,
            language=payload.language or "en"
        )
        return response
    except Exception as e:
        logger.error(f"Assistant error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error processing agronomic inquiry."
        )

