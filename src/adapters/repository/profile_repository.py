import psycopg
import uuid
from src.models.profile import Profile


class ProfileNeo4jRepository:
    def __init__(self, connection: psycopg.AsyncConnection) -> None:
        ...

    async def create_profile(self, profile: Profile) -> None: ...

    async def get_profile(self, id: uuid.UUID) -> Profile: ...

    async def get_profiles(self, ids: list[uuid.UUID]) -> list[Profile]: ...

    async def update_profile(
        self, profile: Profile) -> list[Profile, Profile]: ...
