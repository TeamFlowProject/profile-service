from fastapi import APIRouter

from src.services.profile_service import ProfileService


def create_profile_router(profile_service: ProfileService) -> APIRouter:
    ...
