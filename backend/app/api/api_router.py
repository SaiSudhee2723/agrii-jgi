from fastapi import APIRouter
from app.api.endpoints import (
    soil,
    crop,
    irrigation,
    weather,
    market,
    community,
    auth,
    overview,
    assistant
)

api_router = APIRouter()

api_router.include_router(overview.router, prefix="/overview", tags=["Dashboard Overview & Metrics"])
api_router.include_router(soil.router, prefix="/soil", tags=["Module 1: Soil NPK & Physical Analysis"])
api_router.include_router(crop.router, prefix="/crop", tags=["Module 2: Crop Recommendation"])
api_router.include_router(irrigation.router, prefix="/irrigation", tags=["Module 3: Smart Irrigation"])
api_router.include_router(weather.router, prefix="/weather", tags=["Module 4: Weather Intelligence"])
api_router.include_router(market.router, prefix="/market", tags=["Module 5: Market Intelligence"])
api_router.include_router(community.router, prefix="/community", tags=["Module 6: Community & Discussions"])
api_router.include_router(auth.router, prefix="/auth", tags=["Module 7: User Authentication & Profiles"])
api_router.include_router(assistant.router, prefix="/assistant", tags=["Module 8: AI Agro Assistant"])



