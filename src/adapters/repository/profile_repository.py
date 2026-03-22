import psycopg
from src.models.profile import Profile


class ProfilePostgresRepository:
    def __init__(self, connection: psycopg.AsyncConnection) -> None:
        ...
