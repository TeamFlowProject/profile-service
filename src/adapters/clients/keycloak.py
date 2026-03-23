from keycloak import KeycloakOpenID
from src.models.profile import Profile


class KeycloakClient:
    def __init__(self, base_url: str, client_id: str, realm_name: str,  client_secret_key: str | None) -> None:
        ...
