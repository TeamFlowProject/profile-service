from keycloak import KeycloakAdmin
from src.models.profile import Profile, ProfileCreation


class KeycloakClient:
    def __init__(self, keycloak_admin: KeycloakAdmin) -> None: ...

    async def keycloak_create_user(self, profile: ProfileCreation) -> None: ...
