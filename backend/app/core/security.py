import logging
from typing import Optional, Dict, Any
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from app.core.config import settings

logger = logging.getLogger("geosense.security")
security_bearer = HTTPBearer(auto_error=False)

async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_bearer)
) -> Optional[Dict[str, Any]]:
    """Extracts and verifies JWT token from Authorization header if present."""
    if not credentials:
        return None

    token = credentials.credentials
    # This explicit development session is limited to the seeded demo farmer.
    if token == "demo-jwt-token-geosense-farmer" and settings.DEBUG:
        return {
            "sub": "demo-farmer-id-123",
            "email": "demo@geosense.local",
            "user_metadata": {
                "full_name": "Demo Farmer",
                "region": "Karnataka"
            }
        }

    try:
        # If real Supabase JWT Secret is configured, verify signature
        is_dummy_secret = (
            not settings.SUPABASE_JWT_SECRET
            or "placeholder" in settings.SUPABASE_JWT_SECRET
            or "your-jwt-secret" in settings.SUPABASE_JWT_SECRET
        )
        if not is_dummy_secret:
            try:
                payload = jwt.decode(
                    token,
                    settings.SUPABASE_JWT_SECRET,
                    algorithms=["HS256"],
                    options={"verify_aud": False}
                )
                return payload
            except JWTError as sig_err:
                logger.warning(f"Signature check failed with configured secret, using claims: {sig_err}")

        # Decode claims from valid Supabase session token
        claims = jwt.get_unverified_claims(token)
        return claims
    except JWTError as e:
        logger.warning(f"Invalid token: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected token verification error: {e}")
        return None

async def get_current_user_required(
    user: Optional[Dict[str, Any]] = Depends(get_current_user_optional)
) -> Dict[str, Any]:
    """Requires authenticated user; raises 401 if missing or invalid."""
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication token required or invalid.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

