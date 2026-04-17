import uuid
import pytest
import pytest_asyncio
from datetime import datetime

from src.models.profile import Profile, ProfileCreation, ProfileStatusEnum
from neo4j import AsyncGraphDatabase
import src.adapters.repository.errors as adapters_error
from src.adapters.repository.neo4j.profile_repository import ProfileNeo4jRepository


def _make_profile_creation(mail: str = "test@mail.com") -> ProfileCreation:
    return ProfileCreation(
        id=uuid.uuid4(),
        mail=mail,
        password_hash="hash",
        registration_date=datetime.now(),
        status=ProfileStatusEnum.PENDING,
    )


def _make_profile(mail: str = "test@mail.com", id: uuid.UUID | None = None) -> Profile:
    return Profile(
        id=id or uuid.uuid4(),
        mail=mail,
        password_hash="hash",
        registration_date=datetime.now(),
        name="John",
        surname="Cena",
        status=ProfileStatusEnum.PENDING,
    )


@pytest.mark.integration
class TestProfileRepository:

    @pytest.mark.asyncio
    async def test_create_and_get_profile(self, profile_repository, clean_neo4j):
        profile = _make_profile_creation()
        await profile_repository.create_profile(profile)
        repo_profile = await profile_repository.get_profile(profile.id)

        assert repo_profile.id == profile.id
        assert repo_profile.mail == profile.mail
        assert repo_profile.password_hash == profile.password_hash
        assert repo_profile.registration_date == profile.registration_date
        assert repo_profile.status == profile.status

    @pytest.mark.asyncio
    async def test_create_profile_with_existing_mail(self, profile_repository, clean_neo4j):
        profile1 = _make_profile_creation()
        profile2 = _make_profile_creation(mail=profile1.mail)
        await profile_repository.create_profile(profile1)

        with pytest.raises(adapters_error.ProfileEmailAlreadyTaken):
            await profile_repository.create_profile(profile2)

    @pytest.mark.asyncio
    async def test_get_profile_with_non_existent_id(self, profile_repository, clean_neo4j):
        random_id = uuid.uuid4()
        with pytest.raises(adapters_error.ProfileNotFoundError):
            result = await profile_repository.get_profile(random_id)

    @pytest.mark.asyncio
    async def test_get_profiles(self, profile_repository, clean_neo4j):
        profile1 = _make_profile_creation(mail="test1@mail.com")
        await profile_repository.create_profile(profile1)
        profile2 = _make_profile_creation(mail="test2@mail.com")
        await profile_repository.create_profile(profile2)
        profile3 = _make_profile_creation(mail="test3@mail.com")
        await profile_repository.create_profile(profile3)

        ids = [profile1.id, profile2.id, profile3.id]
        profiles = await profile_repository.get_profiles(ids)

        assert profiles[0].id == profile1.id
        assert profiles[0].mail == profile1.mail
        assert profiles[0].password_hash == profile1.password_hash
        assert profiles[0].registration_date == profile1.registration_date
        assert profiles[0].status == profile1.status

        assert profiles[1].id == profile2.id
        assert profiles[1].mail == profile2.mail
        assert profiles[1].password_hash == profile2.password_hash
        assert profiles[1].registration_date == profile2.registration_date
        assert profiles[1].status == profile2.status

        assert profiles[2].id == profile3.id
        assert profiles[2].mail == profile3.mail
        assert profiles[2].password_hash == profile3.password_hash
        assert profiles[2].registration_date == profile3.registration_date
        assert profiles[2].status == profile3.status

    @pytest.mark.asyncio
    async def test_get_profiles_with_non_existent_id(self, profile_repository, clean_neo4j):
        profile1 = _make_profile_creation()
        await profile_repository.create_profile(profile1)
        random_id = uuid.uuid4()
        ids = [profile1.id, random_id]
        with pytest.raises(adapters_error.ProfileNotFoundError):
            await profile_repository.get_profiles(ids)

    @pytest.mark.asyncio
    async def test_update_profile(self, profile_repository, clean_neo4j):
        creation = _make_profile_creation()
        await profile_repository.create_profile(creation)
        profile = _make_profile(mail=creation.mail, id=creation.id)
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
    async def test_update_non_existent_profile(self, profile_repository, clean_neo4j):
        profile = _make_profile()
        with pytest.raises(adapters_error.ProfileNotFoundError):
            await profile_repository.update_profile(profile)
