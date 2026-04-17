import uuid
from datetime import datetime
from unittest.mock import AsyncMock

import pytest

import src.adapters.repository.errors as adapter_errors
import src.services.errors as service_errors
from src.models.profile import Profile, ProfileCreation, ProfileStatusEnum
from src.services.profile_service import ProfileService


def make_profile_creation(**kwargs) -> ProfileCreation:
    defaults = dict(
        id=uuid.uuid4(),
        mail="test@mail.ru",
        password_hash="hashed_password",
        registration_date=datetime(2026, 1, 1),
        status=ProfileStatusEnum.PENDING,
    )
    defaults.update(kwargs)
    return ProfileCreation(**defaults)  # type: ignore


def make_profile(**kwargs) -> Profile:
    defaults = dict(
        id=uuid.uuid4(),
        mail="test@mail.ru",
        password_hash="hashed_password",
        registration_date=datetime(2026, 1, 1),
        name="Name",
        surname="Surname",
        patronymic="Patronymic",
        stack="Python",
        skills="FastAPI, PostgreSQL",
        experience="1 year",
        desired_role="Backend Developer",
        busyness="Part-time",
        contact_mail="test@example.com",
        contact_number="+1234567890",
        work_place="Test Company",
        work_position="Intern",
        city="Test City",
        portfolio="https://example.com",
        about="Just a test user",
    )
    defaults.update(kwargs)
    return Profile(**defaults)  # type: ignore


def make_small_profile(**kwargs) -> Profile:
    defaults = dict(
        id=uuid.uuid4(),
        mail="test@mail.ru",
        password_hash="hashed_password",
        registration_date=datetime(2026, 1, 1),
    )
    defaults.update(kwargs)
    return Profile(**defaults)  # type: ignore


def make_wrong_profile(**kwargs) -> Profile:
    defaults = dict(
        id=uuid.uuid4(),
        mail="test@mail.ru",
    )
    defaults.update(kwargs)
    return Profile(**defaults)  # type: ignore


@pytest.fixture
def repo():
    return AsyncMock()


@pytest.fixture
def kafka():
    return AsyncMock()


@pytest.fixture
def keycloak():
    return AsyncMock()


@pytest.fixture
def service(repo, kafka, keycloak):
    return ProfileService(
        profile_repository=repo, kafka_producer=kafka, keycloak_connection=keycloak
    )


@pytest.mark.unit
class TestCreateProfile:
    @pytest.mark.asyncio
    async def test_return_id(self, service):
        profile = make_profile_creation()
        result = await service.create_profile(profile)
        assert isinstance(result, uuid.UUID)

    @pytest.mark.asyncio
    async def test_call_repo_and_kafka(self, service, repo, kafka):
        profile = make_profile_creation()
        await service.create_profile(profile)
        repo.create_profile.assert_called_once_with(profile)
        kafka.send_create_profile.assert_called_once_with(profile)

    @pytest.mark.asyncio
    async def test_call_keycloak(self, service, keycloak):
        profile = make_profile_creation()
        await service.create_profile(profile)
        keycloak.keycloak_create_user.assert_called_once_with(profile)

    @pytest.mark.asyncio
    async def test_email_already_taken(self, service, repo):
        repo.create_profile.side_effect = adapter_errors.ProfileEmailAlreadyTaken

        with pytest.raises(service_errors.ProfileEmailAlreadyTaken):
            await service.create_profile(make_profile_creation())


@pytest.mark.unit
class TestUpdateProfile:
    @pytest.mark.asyncio
    async def test_call_repo_and_kafka_with_complete_status(self, service, repo, kafka):
        old_profile = make_profile(status=ProfileStatusEnum.CONFIRMED)
        new_profile = make_profile(
            id=old_profile.id, status=ProfileStatusEnum.COMPLETED
        )
        repo.get_profile.return_value = old_profile
        repo.update_profile.return_value = None

        await service.update_profile(new_profile)

        repo.get_profile.assert_called_once_with(new_profile.id)
        repo.update_profile.assert_called_once_with(new_profile)
        kafka.send_complete_profile.assert_called_once_with(new_profile)
        kafka.send_update_profile.assert_not_called()

    @pytest.mark.asyncio
    async def test_call_repo_and_kafka_with_update_status(self, service, repo, kafka):
        old_profile = make_profile(status=ProfileStatusEnum.COMPLETED)
        new_profile = make_profile(
            id=old_profile.id, status=ProfileStatusEnum.COMPLETED
        )
        repo.get_profile.return_value = old_profile
        repo.update_profile.return_value = None

        await service.update_profile(new_profile)

        repo.get_profile.assert_called_once_with(new_profile.id)
        repo.update_profile.assert_called_once_with(new_profile)
        kafka.send_update_profile.assert_called_once_with(new_profile)
        kafka.send_complete_profile.assert_not_called()

    @pytest.mark.asyncio
    async def test_raises_error_on_completed_to_non_completed_transition(
        self, service, repo
    ):
        old_profile = make_profile(status=ProfileStatusEnum.COMPLETED)
        new_profile = make_profile(id=old_profile.id, status=ProfileStatusEnum.PENDING)
        new_profile.name = ""
        new_profile.surname = ""
        repo.get_profile.return_value = old_profile

        with pytest.raises(service_errors.ProfileStatusTransitionError):
            await service.update_profile(new_profile)

    @pytest.mark.asyncio
    async def test_raises_service_error_when_not_found(self, service, repo, kafka):
        repo.update_profile.side_effect = adapter_errors.ProfileNotFoundError

        with pytest.raises(service_errors.ProfileNotFoundError):
            await service.update_profile(make_profile())

        kafka.send_update_service.assert_not_called()


@pytest.mark.unit
class TestGetProfile:
    @pytest.mark.asyncio
    async def test_returns_profile(self, service, repo):
        profile = make_profile()
        repo.get_profile.return_value = profile

        result = await service.get_profile(profile.id)

        assert result == profile
        repo.get_profile.assert_called_once_with(profile.id)

    @pytest.mark.asyncio
    async def test_raises_profile_not_found(self, service, repo):
        repo.get_profile.side_effect = adapter_errors.ProfileNotFoundError

        with pytest.raises(service_errors.ProfileNotFoundError):
            await service.get_profile(uuid.uuid4())


@pytest.mark.unit
class TestGetProfiles:
    @pytest.mark.asyncio
    async def test_returns_profiles(self, service, repo):
        profile_id = uuid.uuid4()
        profiles = [make_profile(id=profile_id), make_profile(id=profile_id)]
        repo.get_profiles.return_value = profiles

        result = await service.get_profiles(profile_id)

        assert result == profiles
        repo.get_profiles.assert_called_once_with(profile_id)

    @pytest.mark.asyncio
    async def test_raises_profiles_not_found(self, service, repo):
        repo.get_profiles.side_effect = adapter_errors.ProfileNotFoundError

        with pytest.raises(service_errors.ProfileNotFoundError):
            await service.get_profiles(uuid.uuid4())


@pytest.mark.unit
class TestValidation:
    def test_validate_completed_profile(self, service):
        profile = make_profile()
        service._validate(profile)
        assert profile.status == ProfileStatusEnum.COMPLETED

    def test_validate_pending_profile(self, service):
        profile = make_small_profile()
        service._validate(profile)
        assert profile.status == ProfileStatusEnum.PENDING

    def test_validate_profile_error(self, service):
        profile = make_wrong_profile()
        with pytest.raises(service_errors.ProfileCompositionError):
            service._validate(profile)
