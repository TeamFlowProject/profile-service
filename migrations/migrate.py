from pathlib import Path

from neo4j import GraphDatabase
from neo4j_python_migrations.executor import Executor
from src.config import Settings


def run_migrations(settings: Settings) -> None:
    with GraphDatabase.driver(settings.neo4j_uri, auth=settings.neo4j_auth) as driver:
        executor = Executor(driver, migrations_path=Path("migrations"))
        executor.migrate()
