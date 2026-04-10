import uuid
import pytest
import pytest_asyncio
from datetime import datetime

from src.models.profile import Profile, ProfileStatusEnum
from neo4j import AsyncGraphDatabase
import src.adapters.repository.errors as adapters_error
from src.adapters.repository.postgres.profile_repository import ProfileNeo4jRepository


@pytest_asyncio.fixture(scope="function")
async def driver():
    driver = AsyncGraphDatabase.driver(
        "bolt://localhost:7687",
        auth=("neo4j", "password"),
        max_connection_lifetime=3600,
        max_connection_pool_size=10
    )
    try:
        await driver.verify_connectivity()
        yield driver
    finally:
        await driver.close()


@pytest_asyncio.fixture
async def profile_repository(driver):
    return ProfileNeo4jRepository(driver)


@pytest_asyncio.fixture
async def cleanup(driver):
    async with driver.session() as session:
        await session.run("MATCH (n) DETACH DELETE n")
        await session.close()

    yield

    async with driver.session() as session:
        await session.run("MATCH (n) DETACH DELETE n")
        await session.close()


@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_constraints():
    driver = None
    try:
        driver = AsyncGraphDatabase.driver(
            "bolt://localhost:7687",
            auth=("neo4j", "password")
        )
        async with driver.session() as session:
            await session.run(
                """
                CREATE CONSTRAINT profile_mail_unique IF NOT EXISTS
                FOR (p:Profile) REQUIRE p.mail IS UNIQUE
                """
            )
    finally:
        if driver:
            await driver.close()


def _make_profile() -> Profile:
    return Profile(
        id=uuid.uuid4(),
        mail="test@mail.com",
        password_hash="hash",
        registration_date=datetime.now(),

        name="John",
        surname="Cena",

        status=ProfileStatusEnum.PENDING
    )


@pytest.mark.integration
# @pytest.mark.usefixtures("cleanup")
class TestProfileRepository:

    @pytest.mark.asyncio
    async def test_create_and_get_profile(self, profile_repository, driver, cleanup):
        profile = _make_profile()
        await profile_repository.create_profile(profile)
        repo_profile = await profile_repository.get_profile(profile.id)

        assert repo_profile.id == profile.id
        assert repo_profile.mail == profile.mail
        assert repo_profile.password_hash == profile.password_hash
        assert repo_profile.registration_date == profile.registration_date
        assert repo_profile.name == profile.name
        assert repo_profile.surname == profile.surname
        assert repo_profile.status == profile.status

    @pytest.mark.asyncio
    async def test_create_profile_with_existing_mail(self, profile_repository, cleanup):
        profile1 = _make_profile()
        profile2 = _make_profile()
        profile2.mail = profile1.mail
        await profile_repository.create_profile(profile1)

        with pytest.raises(adapters_error.ProfileEmailAlreadyTaken):
            await profile_repository.create_profile(profile2)
