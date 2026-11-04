import logging
from typing import Dict, Any, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas.auth import (
    UserRegisterRequest,
    UserLoginRequest,
    ProfileResponse,
    ProfileUpdateRequest
)
from app.core.config import settings
from app.core.security import get_current_user_required
from app.core.supabase import get_supabase_client, get_supabase_admin_client
from app.core.database import get_sqlite_conn

logger = logging.getLogger("geosense.api.auth")
router = APIRouter()

@router.get("/config", summary="Retrieve public auth configuration")
async def get_auth_config():
    """Returns safe public Supabase configuration for client-side OAuth."""
    is_live = bool(settings.SUPABASE_URL and "placeholder" not in settings.SUPABASE_URL and "your-project" not in settings.SUPABASE_URL)
    return {
        "supabase_url": settings.SUPABASE_URL,
        "supabase_anon_key": settings.SUPABASE_ANON_KEY,
        "is_configured": is_live,
        "demo_enabled": settings.DEBUG
    }

@router.post("/demo", summary="Start a development-only demo session")
async def demo_login():
    """Create the single seeded demo identity for local development and previews."""
    if not settings.DEBUG:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Demo access is disabled.")
    return {
        "access_token": "demo-jwt-token-geosense-farmer",
        "token_type": "bearer",
        "user": {
            "id": "demo-farmer-id-123",
            "email": "demo@geosense.local",
            "full_name": "Demo Farmer",
            "region": "Karnataka",
            "role": "farmer"
        }
    }

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

@router.post("/sync-profile", response_model=ProfileResponse, summary="Sync or provision user profile after Google OAuth")
async def sync_profile(
    profile_data: ProfileUpdateRequest,
    current_user: Dict[str, Any] = Depends(get_current_user_required)
):
    """
    Ensures user profile exists in profiles table after Google OAuth or email sign-in.
    - If user is first-time Google sign-in: creates profile row with name, email, avatar.
    - If user is returning: updates timestamp without duplicating records.
    """
    user_id = current_user.get("sub") or current_user.get("id") or "google-user"
    email = current_user.get("email")
    metadata = current_user.get("user_metadata", {})

    full_name = profile_data.full_name or metadata.get("full_name") or metadata.get("name") or (email.split("@")[0] if email else "Farmer Member")
    avatar_url = profile_data.avatar_url or metadata.get("avatar_url") or metadata.get("picture")
    phone = profile_data.phone or metadata.get("phone")
    region = profile_data.region or metadata.get("region") or "Punjab"
    now_iso = datetime.utcnow().isoformat() + "Z"

    # 1. Supabase Persistence
    supabase = get_supabase_admin_client() or get_supabase_client()
    if supabase and user_id and "demo" not in user_id:
        try:
            res = supabase.table("profiles").select("*").eq("id", user_id).execute()
            if res.data and len(res.data) > 0:
                update_payload = {"updated_at": now_iso}
                if full_name: update_payload["full_name"] = full_name
                if avatar_url: update_payload["avatar_url"] = avatar_url
                if phone: update_payload["phone"] = phone
                if region: update_payload["region"] = region
                up_res = supabase.table("profiles").update(update_payload).eq("id", user_id).execute()
                row = up_res.data[0] if up_res.data else res.data[0]
            else:
                insert_payload = {
                    "id": user_id,
                    "full_name": full_name,
                    "phone": phone,
                    "avatar_url": avatar_url,
                    "role": "farmer",
                    "region": region,
                    "preferred_language": "en",
                    "created_at": now_iso,
                    "updated_at": now_iso
                }
                in_res = supabase.table("profiles").insert(insert_payload).execute()
                row = in_res.data[0] if in_res.data else insert_payload

            return ProfileResponse(
                id=str(row["id"]),
                full_name=row.get("full_name", full_name),
                email=email,
                phone=row.get("phone"),
                avatar_url=row.get("avatar_url"),
                role=row.get("role", "farmer"),
                region=row.get("region"),
                created_at=str(row.get("created_at", now_iso))
            )
        except Exception as e:
            logger.warning(f"Supabase profile sync error: {e}")

    # 2. Local Database Persistence
    try:
        conn = get_sqlite_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM profiles WHERE id = ?", (user_id,))
        existing = cursor.fetchone()
        now_str = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

        if existing:
            cursor.execute("""
                UPDATE profiles 
                SET full_name = ?, avatar_url = coalesce(?, avatar_url), phone = coalesce(?, phone), region = coalesce(?, region), updated_at = ?
                WHERE id = ?
            """, (full_name, avatar_url, phone, region, now_str, user_id))
        else:
            cursor.execute("""
                INSERT INTO profiles (id, full_name, email, phone, avatar_url, role, region, preferred_language, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, 'farmer', ?, 'en', ?, ?)
            """, (user_id, full_name, email, phone, avatar_url, region, now_str, now_str))
        conn.commit()
        conn.close()
    except Exception as e:
        logger.error(f"Local sqlite sync error: {e}")

    return ProfileResponse(
        id=user_id or "demo-user",
        full_name=full_name,
        email=email,
        phone=phone,
        avatar_url=avatar_url,
        role="farmer",
        region=region,
        created_at=now_iso
    )

@router.get("/me", response_model=ProfileResponse, summary="Get current farmer profile")
async def get_my_profile(current_user: Dict[str, Any] = Depends(get_current_user_required)):
    user_id = current_user.get("sub", "") or current_user.get("id", "")
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

    # Fallback to local database
    try:
        conn = get_sqlite_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM profiles WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return ProfileResponse(
                id=str(row["id"]),
                full_name=row["full_name"],
                email=row["email"] or email,
                phone=row["phone"],
                avatar_url=row["avatar_url"],
                role=row["role"] or "farmer",
                region=row["region"] or "Punjab",
                created_at=str(row["created_at"])
            )
    except Exception as e:
        logger.warning(f"Local sqlite load profile warning: {e}")

    # Fallback response from token claims
    metadata = current_user.get("user_metadata", {})
    return ProfileResponse(
        id=user_id or "demo-user",
        full_name=metadata.get("full_name") or metadata.get("name") or email or "Farmer Member",
        email=email,
        phone=metadata.get("phone"),
        avatar_url=metadata.get("avatar_url") or metadata.get("picture"),
        role="farmer",
        region=metadata.get("region") or "Punjab",
        created_at="2026-11-01T00:00:00Z"
    )
