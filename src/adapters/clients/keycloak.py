import aiohttp

from src.models.profile import Profile


class KeycloakClient:
    def __init__(self, base_url: str, session: aiohttp.ClientSession) -> None:
        ...
