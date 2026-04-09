from src.models.profile import Profile, ProfileStatusEnum
from src.services.protocols import ProfileRepository, ProfileKafkaProducer, KeyCloak
import src.services.errors as services_errors
import src.adapters.repository.errors as adapter_errors
import uuid


class ProfileService:
    def __init__(
        self,
        profile_repository: ProfileRepository,
        kafka_producer: ProfileKafkaProducer,
        keycloak_connection: KeyCloak,
    ) -> None:
        self._profile_repository = profile_repository
        self._kafka_producer = kafka_producer
        self._keycloak_connection = keycloak_connection

    async def create_profile(self, profile: Profile) -> uuid.UUID:
        """
        Create a new user profile

        Args:
            profile (Profile): The user profile to create

        Returns:
            uuid.UUID: The id of the created profile
        """
        profile.id = uuid.uuid4()
        self._validate(profile)

        try:
            await self._profile_repository.create_profile(profile)
            await self._kafka_producer.send_create_profile(profile)
            await self._keycloak_connection.keycloak_create_user(profile)
        except adapter_errors.ProfileEmailAlreadyTaken as e:
            raise services_errors.ProfileEmailAlreadyTaken(
                "Profile with given email already exists."
            ) from e
        return profile.id

    async def get_profile(self, id: uuid.UUID) -> Profile:
        """
        Get a profile by ID

        Args:
            uuid.UUID: The ID of the profile to get

        Returns:
            profile (Profile): The profile with the given ID

        Raises:
            ProfileNotFoundError: If the profile could not be found
        """
        try:
            profile = await self._profile_repository.get_profile(id)
            return profile
        except adapter_errors.ProfileNotFoundError as e:
            raise services_errors.ProfileNotFoundError(
                "Couldn't find profile by given ID"
            ) from e

    async def get_profiles(self, ids: list[uuid.UUID]) -> list[Profile]:
        """
        Get all profile by list of IDs

        Args:
            ids (list[uuid.UUID]): The list of profiles's IDs to get

        Returns:
            profiles: (list[Profile]): The list of profiles with the given IDs

        Raises:
            ProfileNotFoundError: If one of profiles could not be found
        """
        try:
            return await self._profile_repository.get_profiles(ids)
        except adapter_errors.ProfileNotFoundError as e:
            raise services_errors.ProfileNotFoundError(
                "Couldn't find one of profiles by given ID"
            ) from e

    async def update_profile(self, profile: Profile) -> None:
        """
        Update the user profile

        Args:
            profile (Profile): The user profile to update

        Raises:
            ProfileNotFoundError: If the profile could not be updated
        """
        try:
            profile_old = await self._profile_repository.get_profile(profile.id)
            self._validate(profile)
            await self._profile_repository.update_profile(profile)
            if (
                profile_old.status != ProfileStatusEnum.COMPLETED
                and profile.status == ProfileStatusEnum.COMPLETED
            ):
                await self._kafka_producer.send_complete_profile(profile)
            else:
                await self._kafka_producer.send_update_profile(profile)
        except adapter_errors.ProfileNotFoundError as e:
            raise services_errors.ProfileNotFoundError(
                "Failed to update profile"
            ) from e

    def _validate(self, profile: Profile) -> None:
        """
        Assign profile status based on the current profile content

        Args:
            profile (Profile): The user profile to validate

        Raises:
            ProfileCompositionError: If the profile field are wrong and no status can be assign
        """
        if all(
            [
                profile.id,
                profile.registration_date,
                profile.mail,
                profile.password_hash,
                profile.name,
                profile.surname,
                profile.patronymic,
                profile.stack,
                profile.skills,
                profile.experience,
                profile.desired_role,
                profile.busyness,
                profile.contact_mail,
                profile.contact_number,
                profile.work_place,
                profile.work_position,
                profile.city,
                profile.portfolio,
                profile.about,
            ]
        ):
            profile.status = ProfileStatusEnum.COMPLETED
        elif all(
            [profile.id, profile.mail, profile.password_hash, profile.registration_date]
        ):
            profile.status = ProfileStatusEnum.PENDING
        else:
            raise services_errors.ProfileCompositionError(
                "Profile composition is invalid"
            )
