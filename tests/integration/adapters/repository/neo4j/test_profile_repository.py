import uuid
import pytest
import pytest_asyncio
from datetime import datetime

from src.models.profile import Profile, ProfileStatusEnum
from neo4j import AsyncGraphDatabase
import src.adapters.repository.errors as adapters_error
from src.adapters.repository.neo4j.profile_repository import ProfileNeo4jRepository


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

    @pytest.mark.asyncio
    async def test_get_profile_with_non_existent_id(self, profile_repository, cleanup):
        random_id = uuid.uuid4()
        with pytest.raises(adapters_error.ProfileNotFoundError):
            result = await profile_repository.get_profile(random_id)

    @pytest.mark.asyncio
    async def test_get_profiles(self, profile_repository, driver, cleanup):
        profile1 = _make_profile()
        await profile_repository.create_profile(profile1)
        profile2 = _make_profile()
        await profile_repository.create_profile(profile1)
        profile3 = _make_profile()
        await profile_repository.create_profile(profile1)

        ids = [profile1.id, profile2.id, profile3.id]
        profiles = profile_repository.get_profiles(ids)

        assert profiles[0].id == profile1.id
        assert profiles[0].mail == profile1.mail
        assert profiles[0].password_hash == profile1.password_hash
        assert profiles[0].registration_date == profile1.registration_date
        assert profiles[0].name == profile1.name
        assert profiles[0].surname == profile1.surname
        assert profiles[0].status == profile1.status

        assert profiles[1].id == profile2.id
        assert profiles[1].mail == profile2.mail
        assert profiles[1].password_hash == profile2.password_hash
        assert profiles[1].registration_date == profile2.registration_date
        assert profiles[1].name == profile2.name
        assert profiles[1].surname == profile2.surname
        assert profiles[1].status == profile2.status

        assert profiles[2].id == profile3.id
        assert profiles[2].mail == profile3.mail
        assert profiles[2].password_hash == profile3.password_hash
        assert profiles[2].registration_date == profile3.registration_date
        assert profiles[2].name == profile3.name
        assert profiles[2].surname == profile3.surname
        assert profiles[2].status == profile3.status

    @pytest.mark.asyncio
    async def test_get_profiles_with_non_existent_id(self, profile_repository, cleanup):
        profile1 = _make_profile()
        await profile_repository.create_profile(profile1)
        random_id = uuid.uuid4()
        ids = [profile1, random_id]
        with pytest.raises(adapters_error.ProfileNotFoundError):
            profiles = await profile_repository.get_profiles(ids)

    @pytest.mark.asyncio
    async def test_update_profile(self, profile_repository, driver, cleanup):
        profile = _make_profile()
        await profile_repository.create_profile(profile)
        profile.name = "Evdak"
        profile.surname = "Cherpack"
        await profile_repository.update_profile(profile)
        bd_profile = await profile_repository.get_profile(profile.id)

        assert bd_profile.id == profile.id
        assert bd_profile.mail == profile.mail
        assert bd_profile.password_hash == profile.password_hash
        assert bd_profile.registration_date == profile.registration_date
        assert bd_profile.name == profile.name
        assert bd_profile.surname == profile.surname
        assert bd_profile.status == profile.status

    @pytest.mark.asyncio
    async def test_update_non_existent_profile(self, profile_repository, driver, cleanup):
        profile = _make_profile()
        with pytest.raises(adapters_error.ProfileNotFoundError):
            await profile_repository.update(profile)
