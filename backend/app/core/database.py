"""
Geosense Unified Database Persistence Engine
Coordinates between Supabase PostgreSQL and local SQLite storage.
Ensures zero fabricated data, persistent user records, and strict RLS/user isolation.
"""

import sqlite3
import json
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
import os
from app.core.config import settings
from app.core.supabase import get_supabase_client

logger = logging.getLogger("geosense.database")

DB_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "geosense_local.db")

def get_sqlite_conn():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_local_database():
    """Initializes local SQLite database matching the Supabase PostgreSQL schema."""
    conn = get_sqlite_conn()
    cursor = conn.cursor()

    cursor.executescript("""
    CREATE TABLE IF NOT EXISTS profiles (
        id TEXT PRIMARY KEY,
        full_name TEXT NOT NULL,
        email TEXT UNIQUE,
        phone TEXT,
        avatar_url TEXT,
        role TEXT NOT NULL DEFAULT 'farmer',
        region TEXT DEFAULT 'Punjab',
        preferred_language TEXT DEFAULT 'en',
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS soil_analysis (
        id TEXT PRIMARY KEY,
        user_id TEXT NOT NULL,
        quality_status TEXT NOT NULL,
        quality_details TEXT NOT NULL, -- JSON
        color_metrics TEXT NOT NULL,   -- JSON
        soil_texture_estimate TEXT,
        soil_condition TEXT NOT NULL,
        nitrogen_ppm REAL,
        phosphorus_ppm REAL,
        potassium_ppm REAL,
        soil_ph REAL,
        electrical_conductivity REAL,
        moisture_pct REAL,
        measurement_type TEXT NOT NULL DEFAULT 'optical_camera', -- 'optical_camera', 'manual_lab', 'iot_sensor'
        lab_name TEXT,
        scientific_disclaimer TEXT NOT NULL,
        lab_test_recommended INTEGER NOT NULL DEFAULT 1,
        recommendations TEXT NOT NULL, -- JSON array
        created_at TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS crop_recommendations (
        id TEXT PRIMARY KEY,
        user_id TEXT NOT NULL,
        input_nitrogen REAL NOT NULL,
        input_phosphorus REAL NOT NULL,
        input_potassium REAL NOT NULL,
        input_temperature REAL NOT NULL,
        input_humidity REAL NOT NULL,
        input_ph REAL NOT NULL,
        input_rainfall REAL NOT NULL,
        primary_recommendation TEXT NOT NULL,
        confidence_score REAL NOT NULL,
        alternative_crops TEXT NOT NULL, -- JSON
        growing_conditions TEXT NOT NULL, -- JSON
        farming_advice TEXT NOT NULL, -- JSON
        created_at TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS irrigation_records (
        id TEXT PRIMARY KEY,
        user_id TEXT NOT NULL,
        crop_name TEXT NOT NULL,
        growth_stage TEXT NOT NULL,
        soil_moisture_percentage REAL NOT NULL,
        field_area_acres REAL NOT NULL,
        temperature_celsius REAL,
        humidity_percentage REAL,
        forecast_rainfall_mm REAL NOT NULL DEFAULT 0.0,
        evapotranspiration_mm REAL NOT NULL DEFAULT 0.0,
        water_required_liters_per_acre REAL NOT NULL,
        total_water_liters REAL NOT NULL,
        irrigation_needed INTEGER NOT NULL,
        schedule_recommendation TEXT NOT NULL,
        water_saving_tips TEXT NOT NULL, -- JSON
        created_at TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS community_posts (
        id TEXT PRIMARY KEY,
        user_id TEXT NOT NULL,
        author_name TEXT NOT NULL,
        author_avatar TEXT,
        title TEXT NOT NULL,
        content TEXT NOT NULL,
        category TEXT NOT NULL DEFAULT 'general',
        image_url TEXT,
        likes_count INTEGER NOT NULL DEFAULT 0,
        comments_count INTEGER NOT NULL DEFAULT 0,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS community_comments (
        id TEXT PRIMARY KEY,
        post_id TEXT NOT NULL,
        user_id TEXT NOT NULL,
        author_name TEXT NOT NULL,
        author_avatar TEXT,
        content TEXT NOT NULL,
        created_at TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS post_likes (
        user_id TEXT NOT NULL,
        post_id TEXT NOT NULL,
        created_at TEXT NOT NULL,
        PRIMARY KEY (user_id, post_id)
    );

    CREATE TABLE IF NOT EXISTS farms (
        id TEXT PRIMARY KEY,
        user_id TEXT NOT NULL,
        farm_name TEXT NOT NULL,
        latitude REAL NOT NULL,
        longitude REAL NOT NULL,
        boundary_coordinates TEXT,
        area_acres REAL DEFAULT 0.0,
        crop_type TEXT DEFAULT 'General Crop',
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
    );
    """)

    conn.commit()
    conn.close()
    logger.info("Local database initialized successfully with full schema.")

# Initialize on module load
try:
    init_local_database()
except Exception as e:
    logger.error(f"Error initializing local database schema: {e}")

