import logging
from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas.auth import (
    UserRegisterRequest,
    UserLoginRequest,
    ProfileResponse,
    ProfileUpdateRequest
)
from app.core.security import get_current_user_required
from app.core.supabase import get_supabase_client, get_supabase_admin_client

logger = logging.getLogger("geosense.api.auth")
router = APIRouter()

@router.post("/register", summary="Register new farmer account via Supabase Auth")
async def register_user(payload: UserRegisterRequest):
    """
    Module 7: Register user with Supabase Auth and initialize farmer profile.
    """
    supabase = get_supabase_client()
    if not supabase:
        return {
            "message": "Demo mode: user registration simulated successfully.",
            "user": {
                "id": "demo-farmer-id-123",
                "email": payload.email,
                "full_name": payload.full_name
            }
        }

    try:
        res = supabase.auth.sign_up({
            "email": payload.email,
            "password": payload.password,
            "options": {
                "data": {
                    "full_name": payload.full_name,
                    "phone": payload.phone,
                    "region": payload.region
                }
            }
        })
        return {
            "message": "Registration successful. Please verify email if confirmation is enabled.",
            "session": res.session,
            "user": res.user
        }
    except Exception as e:
        logger.error(f"Registration error: {e}")
        err_msg = str(e)
        if "getaddrinfo" in err_msg or "Failed to resolve" in err_msg or "Name or service not known" in err_msg:
            err_msg = f"Cannot connect to Supabase: '{settings.SUPABASE_URL}' could not be resolved. Please check the project URL in your backend/.env file."
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=err_msg)

@router.post("/login", summary="Sign in user and return JWT session")
async def login_user(payload: UserLoginRequest):
    supabase = get_supabase_client()
    if not supabase:
        return {
            "access_token": "demo-jwt-token-geosense-farmer",
            "token_type": "bearer",
            "user": {
                "id": "demo-farmer-id-123",
                "email": payload.email,
                "full_name": "Demo Farmer"
            }
        }

    try:
        res = supabase.auth.sign_in_with_password({
            "email": payload.email,
            "password": payload.password
        })
        return {
            "access_token": res.session.access_token,
            "refresh_token": res.session.refresh_token,
            "token_type": "bearer",
            "user": res.user
        }
    except Exception as e:
        logger.error(f"Login error: {e}")
        err_msg = str(e)
        if "getaddrinfo" in err_msg or "Failed to resolve" in err_msg:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Cannot reach Supabase host at '{settings.SUPABASE_URL}'. Please verify the URL in backend/.env."
            )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password credentials."
        )

@router.get("/me", response_model=ProfileResponse, summary="Get current farmer profile")
async def get_my_profile(current_user: Dict[str, Any] = Depends(get_current_user_required)):
    user_id = current_user.get("sub", "")
    email = current_user.get("email")

    supabase = get_supabase_client()
    if supabase and user_id:
        try:
            res = supabase.table("profiles").select("*").eq("id", user_id).single().execute()
            if res.data:
                row = res.data
                return ProfileResponse(
                    id=str(row["id"]),
                    full_name=row.get("full_name", "Farmer"),
                    email=email,
                    phone=row.get("phone"),
                    avatar_url=row.get("avatar_url"),
                    role=row.get("role", "farmer"),
                    region=row.get("region"),
                    created_at=row.get("created_at", "")
                )
        except Exception as e:
            logger.warning(f"Could not load profile from Supabase: {e}")

    # Fallback response from token claims
    metadata = current_user.get("user_metadata", {})
    return ProfileResponse(
        id=user_id or "demo-user",
        full_name=metadata.get("full_name") or email or "Farmer Member",
        email=email,
        phone=metadata.get("phone"),
        role="farmer",
        region=metadata.get("region"),
        created_at="2026-11-01T00:00:00Z"
    )

