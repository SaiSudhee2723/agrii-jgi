import logging
import uuid
import json
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas.farm import FarmCreate, FarmUpdate, FarmResponse
from app.core.security import get_current_user_required
from app.core.supabase import get_supabase_admin_client, get_supabase_client
from app.core.database import get_sqlite_conn

logger = logging.getLogger("geosense.api.farms")
router = APIRouter()

def _parse_boundary(raw: Any) -> List[List[float]]:
    if not raw:
        return []
    if isinstance(raw, list):
        return raw
    if isinstance(raw, str):
        try:
            parsed = json.loads(raw)
            return parsed if isinstance(parsed, list) else []
        except Exception:
            return []
    return []

@router.get("", response_model=List[FarmResponse], summary="List all saved farm locations for the current user")
async def list_farms(
    current_user: Dict[str, Any] = Depends(get_current_user_required)
):
    user_id = current_user.get("sub") or current_user.get("id") or "anonymous"
    farms: List[Dict[str, Any]] = []

    # 1. Supabase Query
    supabase = get_supabase_admin_client() or get_supabase_client()
    if supabase and "demo" not in user_id:
        try:
            res = supabase.table("farms").select("*").eq("user_id", user_id).order("created_at", desc=True).execute()
            if res.data is not None:
                for row in res.data:
                    farms.append({
                        "id": str(row["id"]),
                        "user_id": str(row["user_id"]),
                        "farm_name": row.get("farm_name", "My Farm"),
                        "latitude": float(row.get("latitude", 0.0)),
                        "longitude": float(row.get("longitude", 0.0)),
                        "boundary_coordinates": _parse_boundary(row.get("boundary_coordinates")),
                        "area_acres": float(row.get("area_acres") or 0.0),
                        "crop_type": row.get("crop_type", "General Crop"),
                        "created_at": str(row.get("created_at", "")),
                        "updated_at": str(row.get("updated_at", ""))
                    })
                return farms
        except Exception as e:
            logger.warning(f"Supabase list farms query failed, falling back to local DB: {e}")

    # 2. Local SQLite Fallback
    try:
        conn = get_sqlite_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM farms WHERE user_id = ? ORDER BY created_at DESC", (user_id,))
        rows = cursor.fetchall()
        for r in rows:
            farms.append({
                "id": str(r["id"]),
                "user_id": str(r["user_id"]),
                "farm_name": r["farm_name"],
                "latitude": float(r["latitude"]),
                "longitude": float(r["longitude"]),
                "boundary_coordinates": _parse_boundary(r["boundary_coordinates"]),
                "area_acres": float(r["area_acres"] or 0.0),
                "crop_type": r["crop_type"] or "General Crop",
                "created_at": str(r["created_at"]),
                "updated_at": str(r["updated_at"])
            })
        conn.close()
    except Exception as e:
        logger.error(f"Local SQLite list farms failed: {e}")

    return farms

@router.post("", response_model=FarmResponse, status_code=status.HTTP_201_CREATED, summary="Save a new farm location with boundary")
async def create_farm(
    payload: FarmCreate,
    current_user: Dict[str, Any] = Depends(get_current_user_required)
):
    user_id = current_user.get("sub") or current_user.get("id") or "anonymous"
    farm_id = str(uuid.uuid4())
    now_iso = datetime.now(timezone.utc).isoformat()
    boundary_json = json.dumps(payload.boundary_coordinates or [])

    record = {
        "id": farm_id,
        "user_id": user_id,
        "farm_name": payload.farm_name,
        "latitude": payload.latitude,
        "longitude": payload.longitude,
        "boundary_coordinates": payload.boundary_coordinates or [],
        "area_acres": round(payload.area_acres or 0.0, 2),
        "crop_type": payload.crop_type or "General Crop",
        "created_at": now_iso,
        "updated_at": now_iso
    }

    # 1. Supabase Insert
    supabase = get_supabase_admin_client() or get_supabase_client()
    if supabase and "demo" not in user_id:
        try:
            sp_payload = {
                "id": farm_id,
                "user_id": user_id,
                "farm_name": payload.farm_name,
                "latitude": payload.latitude,
                "longitude": payload.longitude,
                "boundary_coordinates": payload.boundary_coordinates or [],
                "area_acres": round(payload.area_acres or 0.0, 2),
                "crop_type": payload.crop_type or "General Crop",
                "created_at": now_iso,
                "updated_at": now_iso
            }
            res = supabase.table("farms").insert(sp_payload).execute()
            if res.data and len(res.data) > 0:
                logger.info(f"Farm successfully saved to Supabase: {farm_id}")
        except Exception as e:
            logger.warning(f"Supabase farm insert notice (saving locally): {e}")

    # 2. Local SQLite Persistence
    try:
        conn = get_sqlite_conn()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO farms (id, user_id, farm_name, latitude, longitude, boundary_coordinates, area_acres, crop_type, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            farm_id,
            user_id,
            payload.farm_name,
            payload.latitude,
            payload.longitude,
            boundary_json,
            record["area_acres"],
            record["crop_type"],
            now_iso,
            now_iso
        ))
        conn.commit()
        conn.close()
    except Exception as e:
        logger.error(f"Local SQLite farm insert error: {e}")

    return record

@router.get("/{farm_id}", response_model=FarmResponse, summary="Get farm location by ID")
async def get_farm(
    farm_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user_required)
):
    user_id = current_user.get("sub") or current_user.get("id") or "anonymous"

    # Try Supabase
    supabase = get_supabase_admin_client() or get_supabase_client()
    if supabase and "demo" not in user_id:
        try:
            res = supabase.table("farms").select("*").eq("id", farm_id).eq("user_id", user_id).execute()
            if res.data and len(res.data) > 0:
                row = res.data[0]
                return {
                    "id": str(row["id"]),
                    "user_id": str(row["user_id"]),
                    "farm_name": row.get("farm_name"),
                    "latitude": float(row.get("latitude")),
                    "longitude": float(row.get("longitude")),
                    "boundary_coordinates": _parse_boundary(row.get("boundary_coordinates")),
                    "area_acres": float(row.get("area_acres") or 0.0),
                    "crop_type": row.get("crop_type"),
                    "created_at": str(row.get("created_at")),
                    "updated_at": str(row.get("updated_at"))
                }
        except Exception as e:
            logger.warning(f"Supabase get farm error: {e}")

    # Fallback SQLite
    conn = get_sqlite_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM farms WHERE id = ? AND user_id = ?", (farm_id, user_id))
    r = cursor.fetchone()
    conn.close()

    if not r:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Farm location not found.")

    return {
        "id": str(r["id"]),
        "user_id": str(r["user_id"]),
        "farm_name": r["farm_name"],
        "latitude": float(r["latitude"]),
        "longitude": float(r["longitude"]),
        "boundary_coordinates": _parse_boundary(r["boundary_coordinates"]),
        "area_acres": float(r["area_acres"] or 0.0),
        "crop_type": r["crop_type"],
        "created_at": str(r["created_at"]),
        "updated_at": str(r["updated_at"])
    }

@router.put("/{farm_id}", response_model=FarmResponse, summary="Update an existing farm location or boundary")
async def update_farm(
    farm_id: str,
    payload: FarmUpdate,
    current_user: Dict[str, Any] = Depends(get_current_user_required)
):
    user_id = current_user.get("sub") or current_user.get("id") or "anonymous"
    now_iso = datetime.now(timezone.utc).isoformat()

    # Verify existence
    existing = await get_farm(farm_id, current_user)
    updated_name = payload.farm_name if payload.farm_name is not None else existing.get("farm_name")
    updated_lat = payload.latitude if payload.latitude is not None else existing.get("latitude")
    updated_lon = payload.longitude if payload.longitude is not None else existing.get("longitude")
    updated_boundary = payload.boundary_coordinates if payload.boundary_coordinates is not None else existing.get("boundary_coordinates", [])
    updated_area = payload.area_acres if payload.area_acres is not None else existing.get("area_acres", 0.0)
    updated_crop = payload.crop_type if payload.crop_type is not None else existing.get("crop_type", "General Crop")

    # 1. Supabase Update
    supabase = get_supabase_admin_client() or get_supabase_client()
    if supabase and "demo" not in user_id:
        try:
            up_dict = {
                "farm_name": updated_name,
                "latitude": updated_lat,
                "longitude": updated_lon,
                "boundary_coordinates": updated_boundary,
                "area_acres": updated_area,
                "crop_type": updated_crop,
                "updated_at": now_iso
            }
            supabase.table("farms").update(up_dict).eq("id", farm_id).eq("user_id", user_id).execute()
        except Exception as e:
            logger.warning(f"Supabase farm update notice: {e}")

    # 2. Local SQLite Update
    try:
        conn = get_sqlite_conn()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE farms SET farm_name = ?, latitude = ?, longitude = ?, boundary_coordinates = ?, area_acres = ?, crop_type = ?, updated_at = ?
            WHERE id = ? AND user_id = ?
        """, (
            updated_name,
            updated_lat,
            updated_lon,
            json.dumps(updated_boundary),
            updated_area,
            updated_crop,
            now_iso,
            farm_id,
            user_id
        ))
        conn.commit()
        conn.close()
    except Exception as e:
        logger.error(f"Local SQLite farm update error: {e}")

    return {
        "id": farm_id,
        "user_id": user_id,
        "farm_name": updated_name,
        "latitude": updated_lat,
        "longitude": updated_lon,
        "boundary_coordinates": updated_boundary,
        "area_acres": updated_area,
        "crop_type": updated_crop,
        "created_at": existing.get("created_at", now_iso),
        "updated_at": now_iso
    }

@router.delete("/{farm_id}", summary="Delete a saved farm location")
async def delete_farm(
    farm_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user_required)
):
    user_id = current_user.get("sub") or current_user.get("id") or "anonymous"

    # Supabase Delete
    supabase = get_supabase_admin_client() or get_supabase_client()
    if supabase and "demo" not in user_id:
        try:
            supabase.table("farms").delete().eq("id", farm_id).eq("user_id", user_id).execute()
        except Exception as e:
            logger.warning(f"Supabase delete notice: {e}")

    # SQLite Delete
    try:
        conn = get_sqlite_conn()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM farms WHERE id = ? AND user_id = ?", (farm_id, user_id))
        conn.commit()
        conn.close()
    except Exception as e:
        logger.error(f"Local SQLite delete farm error: {e}")

    return {"message": "Farm location deleted successfully.", "id": farm_id}
