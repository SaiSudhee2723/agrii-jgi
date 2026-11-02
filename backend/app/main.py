import logging
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.core.config import settings
from app.api.api_router import api_router

# Configure logging
logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("geosense")

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Software-only AI & IoT backend for Geosense Smart Agriculture Intelligent System.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# CORS Configuration
origins = settings.cors_origin_list
if "*" not in origins:
    # Ensure standard local development ports are permitted
    for port in [8080, 5500, 3000, 5173, 8000, 8001]:
        origins.append(f"http://localhost:{port}")
        origins.append(f"http://127.0.0.1:{port}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=list(set(origins)),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Modular Routers
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/health", tags=["Health"])
async def health_check():
    """System health and operational status check."""
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": "1.0.0",
        "environment": "development" if settings.DEBUG else "production"
    }

@app.get("/", tags=["Root"])
async def root():
    """Root entrypoint providing links to interactive documentation."""
    return {
        "name": settings.PROJECT_NAME,
        "documentation": "/docs",
        "api_v1": settings.API_V1_STR,
        "modules": [
            "Module 1: Soil NPK & Physical Analysis (/api/v1/soil)",
            "Module 2: Crop Recommendation (/api/v1/crop)",
            "Module 3: Smart Irrigation (/api/v1/irrigation)",
            "Module 4: Weather Intelligence (/api/v1/weather)",
            "Module 5: Market Intelligence (/api/v1/market)",
            "Module 6: Community & Discussions (/api/v1/community)",
            "Module 7: User Authentication & Profiles (/api/v1/auth)"
        ]
    }

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error processing {request.method} {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An internal server error occurred. Please contact support or check server logs."}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=settings.HOST, port=settings.PORT, reload=settings.DEBUG)

