from fastapi import APIRouter

from src.services.profile_service import ProfileService


def create_profile_router(profile_service: ProfileService) -> APIRouter:
    router = APIRouter(prefix="/profiles", tags=["profiles"])

    @router.get("/health")
    async def health_check():
        return {"status": "healthy", "service": "profile-service"}

    return router
