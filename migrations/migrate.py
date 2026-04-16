from neo4j_migrations import MigrationClient
from src.config import Settings


def run_migrations(settings: Settings) -> None:
    client = MigrationClient(
        uri=settings.neo4j_uri,
        auth=settings.neo4j_auth,
        migration_dir="migrations",
    )
    client.apply()
