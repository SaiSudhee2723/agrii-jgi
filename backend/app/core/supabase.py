import logging
from typing import Optional
from supabase import create_client, Client
from app.core.config import settings

logger = logging.getLogger("geosense.supabase")

_supabase_client: Optional[Client] = None
_supabase_admin_client: Optional[Client] = None

def get_supabase_client() -> Optional[Client]:
    """Returns standard Supabase client with anon key."""
    global _supabase_client
    if _supabase_client is not None:
        return _supabase_client

    if not settings.SUPABASE_URL or "placeholder" in settings.SUPABASE_URL:
        logger.warning("Supabase URL is not configured. Running in unconfigured/offline mode.")
        return None

    try:
        _supabase_client = create_client(settings.SUPABASE_URL, settings.SUPABASE_ANON_KEY)
        return _supabase_client
    except Exception as e:
        logger.error(f"Failed to initialize Supabase client: {e}")
        return None

def get_supabase_admin_client() -> Optional[Client]:
    """Returns admin Supabase client with service role key for elevated server-side operations."""
    global _supabase_admin_client
    if _supabase_admin_client is not None:
        return _supabase_admin_client

    if not settings.SUPABASE_URL or "placeholder" in settings.SUPABASE_URL:
        return None

    try:
        _supabase_admin_client = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_ROLE_KEY)
        return _supabase_admin_client
    except Exception as e:
        logger.error(f"Failed to initialize Supabase admin client: {e}")
        return None

