import os
from typing import List
from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    PROJECT_NAME: str = "Geosense Smart Agriculture API"
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = True
    PORT: int = 8000
    HOST: str = "0.0.0.0"

    # CORS
    CORS_ORIGINS: str = "http://localhost:8080,http://127.0.0.1:8080,http://localhost:3000,http://127.0.0.1:5500"

    # Supabase
    SUPABASE_URL: str = Field(default="https://placeholder-project.supabase.co")
    SUPABASE_ANON_KEY: str = Field(default="placeholder-anon-key")
    SUPABASE_SERVICE_ROLE_KEY: str = Field(default="placeholder-service-role-key")
    SUPABASE_JWT_SECRET: str = Field(default="placeholder-jwt-secret")

    # Weather & Market
    OPENWEATHER_API_KEY: str = Field(default="")
    MARKET_DATA_MODE: str = Field(default="demo")

    @property
    def cors_origin_list(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "allow"

settings = Settings()

