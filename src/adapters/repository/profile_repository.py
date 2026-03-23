import psycopg
from src.models.profile import Profile


class ProfileNeo4jRepository:
    def __init__(self, connection: psycopg.AsyncConnection) -> None:
        ...
