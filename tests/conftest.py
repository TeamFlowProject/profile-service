import pytest
import pytest_asyncio
from testcontainers.neo4j import Neo4jContainer
from neo4j import AsyncGraphDatabase
from src.adapters.repository.neo4j.profile_repository import ProfileNeo4jRepository


@pytest.fixture(scope="session")
def neo4j_container():
    with Neo4jContainer("neo4j:5") as neo4j:
        neo4j.with_admin_password("test_password")

        neo4j.start()

        uri = f"bolt://{neo4j.get_container_host_ip()}:{neo4j.get_exposed_port(7687)}"
        user = "neo4j"
        password = "test_password"

        async def setup_neo4j():
            driver = AsyncGraphDatabase.driver(uri, auth=(user, password))
            async with driver.session() as session:
                await session.run("""
                    CREATE CONSTRAINT profile_mail_unique IF NOT EXISTS
                    FOR (p:Profile) REQUIRE p.mail IS UNIQUE
                """)
            await driver.close()

        import asyncio
        asyncio.run(setup_neo4j())

        yield {
            "uri": uri,
            "user": user,
            "password": password
        }


@pytest_asyncio.fixture(scope="function")
async def neo4j_driver(neo4j_container):
    driver = AsyncGraphDatabase.driver(
        neo4j_container["uri"],
        auth=(neo4j_container["user"], neo4j_container["password"]),
        max_connection_pool_size=10,
        connection_acquisition_timeout=30
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
