import pytest
import pytest_asyncio
from testcontainers.neo4j import Neo4jContainer
from neo4j import AsyncGraphDatabase
from migrations.migrate import run_migrations
from src.config import Settings
from src.adapters.repository.neo4j.profile_repository import ProfileNeo4jRepository


@pytest.fixture(scope="session")
def neo4j_container():
    neo4j = Neo4jContainer("neo4j:5").with_env("NEO4J_PLUGINS", "[]")
    neo4j.start()

    try:
        uri = neo4j.get_connection_url()

        settings = Settings(
            neo4j_uri=uri,
            neo4j_auth=(neo4j.username, neo4j.password),
        )
        run_migrations(settings)

        yield {
            "uri": uri,
            "user": neo4j.username,
            "password": neo4j.password,
        }
    finally:
        neo4j.stop()


@pytest_asyncio.fixture(scope="function")
async def neo4j_driver(neo4j_container):
    driver = AsyncGraphDatabase.driver(
        neo4j_container["uri"],
        auth=(neo4j_container["user"], neo4j_container["password"]),
        max_connection_pool_size=10,
        connection_acquisition_timeout=30,
    )

    await driver.verify_connectivity()
    yield driver
    await driver.close()


@pytest_asyncio.fixture(scope="function")
async def profile_repository(neo4j_driver):
    return ProfileNeo4jRepository(neo4j_driver)


@pytest_asyncio.fixture(scope="function", autouse=True)
async def clean_neo4j(neo4j_driver):
    async with neo4j_driver.session() as session:
        await session.run("MATCH (n) DETACH DELETE n")

    yield

    async with neo4j_driver.session() as session:
        await session.run("MATCH (n) DETACH DELETE n")
