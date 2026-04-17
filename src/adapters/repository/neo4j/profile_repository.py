import uuid
from neo4j import AsyncDriver, exceptions
from src.models.profile import Profile, ProfileCreation, ProfileStatusEnum
import src.adapters.repository.errors as adapter_errors
from src.adapters.repository.neo4j.queries import (
    CREATE_QUERY,
    GET_PROFILE_QUERY,
    GET_PROFILES_QUERY,
    UPDATE_PROFILE_QUERY,
)


class ProfileNeo4jRepository:
    def __init__(self, driver: AsyncDriver) -> None:
        self._driver = driver

    async def create_profile(self, profile: ProfileCreation) -> None:
        """
        Create a new profile

        Args:
            profile (ProfileCreation): The profile to create

        Raises:
            ProfileEmailAlreadyTaken: If the profile with given mail already exist
        """

        async def tx_func(tx):
            await tx.run(
                CREATE_QUERY, self._convert_profile_creation_to_dictionary(profile)
            )

        try:
            async with self._driver.session() as session:
                await session.execute_write(tx_func)
        except exceptions.ConstraintError:
            raise adapter_errors.ProfileEmailAlreadyTaken(
                f"Profile with mail {profile.mail} already exists"
            )

    async def get_profile(self, id: uuid.UUID) -> Profile:
        """
        Get the profile by id

        Args:
            id (uuid.UUID): The profile id to get

        Returns:
            profile (Profile): The profile got by the given id

        Raises:
            ProfileNotFoundError: If profile with given id doesn't exist
        """

        async def tx_func(tx):
            result = await tx.run(GET_PROFILE_QUERY, {"id": str(id)})

            record = await result.single()

            if record is None:
                return None

            node = record["p"]
            return self._convert_dictionary_to_profile(node)

        async with self._driver.session() as session:
            profile = await session.execute_read(tx_func)

        if profile is None:
            raise adapter_errors.ProfileNotFoundError(
                f"Profile with id {id} doesn't exist"
            )
        else:
            return profile

    async def get_profiles(self, ids: list[uuid.UUID]) -> list[Profile]:
        """
        Get profiles by ids

        Args:
            list(id) (List(uuid.UUID)): The profiles id to get

        Returns:
            list(profiles) (List(Profiles)): List of found profiles

        Raises:
            ProfileNotFoundError: If any of profiles with given ids doesn't exist
        """

        async def tx_func(tx):
            result = await tx.run(GET_PROFILES_QUERY, {"ids": [str(i) for i in ids]})

            profiles = []

            async for record in result:
                node = record["p"]
                profiles.append(self._convert_dictionary_to_profile(node))

            return profiles

        async with self._driver.session() as session:
            profiles = await session.execute_read(tx_func)

        if len(profiles) != len(ids):
            found_ids = {p.id for p in profiles}
            missing_ids = {i for i in ids if i not in found_ids}
            raise adapter_errors.ProfileNotFoundError(
                f"Profiles with ids: {missing_ids} doesn't exist"
            )

        return profiles

    async def update_profile(self, profile: Profile) -> None:
        """
        Update profile parameters

        Args:
            profile (Profile): The profile data to update

        Raises:
            ProfileNotFoundError: If update non-existent profile
        """

        async def tx_func(tx):
            result = await tx.run(
                UPDATE_PROFILE_QUERY, self._convert_profile_to_dictionary(profile)
            )

            record = await result.single()
            return record

        async with self._driver.session() as session:
            record = await session.execute_write(tx_func)

        if record is None:
            raise adapter_errors.ProfileNotFoundError("Given profile doesn't exist")

    @staticmethod
    def _convert_profile_creation_to_dictionary(profile: ProfileCreation) -> dict:
        return {
            "id": str(profile.id),
            "mail": profile.mail,
            "password_hash": profile.password_hash,
            "registration_date": profile.registration_date,
            "status": profile.status.value if profile.status else None,
        }

    @staticmethod
    def _convert_profile_to_dictionary(profile: Profile) -> dict:
        """
        Convert profile model object to a dictionary

        Args:
            profile (Profile): The profile to convert

        Returns:
            dict: Dictionary with profile data
        """
        profile_dict = {
            "id": str(profile.id),
            "mail": profile.mail,
            "password_hash": profile.password_hash,
            "registration_date": profile.registration_date,
            "name": profile.name,
            "surname": profile.surname,
            "patronymic": profile.patronymic,
            "stack": profile.stack,
            "skills": profile.skills,
            "experience": profile.experience,
            "desired_role": profile.desired_role,
            "busyness": profile.busyness,
            "contact_mail": profile.contact_mail,
            "contact_number": profile.contact_number,
            "work_place": profile.work_place,
            "work_position": profile.work_position,
            "city": profile.city,
            "portfolio": profile.portfolio,
            "about": profile.about,
            "status": profile.status.value if profile.status else None,
        }
        return profile_dict

    @staticmethod
    def _convert_dictionary_to_profile(profile_dict: dict) -> Profile:
        """
        Convert profile dictionary to a profile model object

        Args:
            dict: The profile dictionary to convert

        Returns:
            profile (Profile): Profile model object
        """
        profile = Profile(
            id=uuid.UUID(profile_dict["id"]),
            mail=profile_dict["mail"],
            password_hash=profile_dict["password_hash"],
            registration_date=profile_dict["registration_date"],
            name=profile_dict.get("name", ""),
            surname=profile_dict.get("surname", ""),
            patronymic=profile_dict.get("patronymic", ""),
            stack=profile_dict.get("stack", ""),
            skills=profile_dict.get("skills", ""),
            experience=profile_dict.get("experience", ""),
            desired_role=profile_dict.get("desired_role", ""),
            busyness=profile_dict.get("busyness", ""),
            contact_mail=profile_dict.get("contact_mail", ""),
            contact_number=profile_dict.get("contact_number", ""),
            work_place=profile_dict.get("work_place", ""),
            work_position=profile_dict.get("work_position", ""),
            city=profile_dict.get("city", ""),
            portfolio=profile_dict.get("portfolio", ""),
            about=profile_dict.get("about", ""),
            status=ProfileStatusEnum(profile_dict["status"])
            if profile_dict.get("status")
            else None,
        )
        return profile
