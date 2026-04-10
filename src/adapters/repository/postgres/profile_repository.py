import uuid
from neo4j import AsyncDriver, exceptions
from src.models.profile import Profile, ProfileStatusEnum
import src.adapters.repository.errors as adapter_errors
from src.adapters.repository.postgres.queries import (
    CREATE_QUERY,
    GET_PROFILE_QUERY,
    GET_PROFILES_QUERY,
    UPDATE_PROFILE_QUERY
)


class ProfileNeo4jRepository:
    def __init__(self, driver: AsyncDriver) -> None:
        self._driver = driver

    async def create_profile(self, profile: Profile) -> None:
        '''
        Create a new profile

        Args:
            profile (Profile): The profile to create

        Raises:
            ProfileEmailAlreadyTaken: If the profile with given mail already exist
        '''
        async def tx_func(tx):
            await tx.run(
                CREATE_QUERY,
                {
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

                    "status": profile.status.value if profile.status else None
                }
            )

        try:
            async with self._driver.session() as session:
                await session.execute_write(tx_func)
        except exceptions.ConstraintError:
            raise adapter_errors.ProfileEmailAlreadyTaken(
                f"Profile with mail {profile.mail} already exists")

    async def get_profile(self, id: uuid.UUID) -> Profile:
        '''
        Get the profile by id

        Args:
            id (uuid.UUID): The profile id to get

        Raises:
            ProfileNotFoundError: If profile with given id doesn't exist
        '''
        async def tx_func(tx):
            result = await tx.run(
                GET_PROFILE_QUERY,
                {
                    "id": str(id)
                }
            )

            record = await result.single()

            if record is None:
                return None

            node = record["p"]
            return Profile(
                id=uuid.UUID(node["id"]),
                mail=node["mail"],
                password_hash=node["password_hash"],
                registration_date=node["registration_date"],
                name=node.get("name", ""),
                surname=node.get("surname", ""),
                patronymic=node.get("patronymic", ""),
                stack=node.get("stack", ""),
                skills=node.get("skills", ""),
                experience=node.get("experience", ""),
                desired_role=node.get("desired_role", ""),
                busyness=node.get("busyness", ""),
                contact_mail=node.get("contact_mail", ""),
                contact_number=node.get("contact_number", ""),
                work_place=node.get("work_place", ""),
                work_position=node.get("work_position", ""),
                city=node.get("city", ""),
                portfolio=node.get("portfolio", ""),
                about=node.get("about", ""),
                status=ProfileStatusEnum(
                    node["status"]) if node.get("status") else None
            )

        async with self._driver.session() as session:
            profile = await session.execute_read(tx_func)

        if profile is None:
            raise adapter_errors.ProfileNotFoundError(
                f"Profile with id {id} doesn't exist")
        else:
            return profile

    async def get_profiles(self, ids: list[uuid.UUID]) -> list[Profile]:
        '''
        Get profiles by ids

        Args:
            list(id) (list(uuid.UUID)): The profiles id to get

        Raises:
            ProfileNotFoundError: If any of profiles with given ids doesn't exist
        '''
        async def tx_func(tx):
            result = await tx.run(
                GET_PROFILES_QUERY,
                {"ids": [str(i) for i in ids]}
            )

            profiles = []

            async for record in result:
                node = record["p"]
                profiles.append(
                    Profile(
                        id=uuid.UUID(node["id"]),
                        mail=node["mail"],
                        password_hash=node["password_hash"],
                        registration_date=node["registration_date"],
                        name=node.get("name", ""),
                        surname=node.get("surname", ""),
                        patronymic=node.get("patronymic", ""),
                        stack=node.get("stack", ""),
                        skills=node.get("skills", ""),
                        experience=node.get("experience", ""),
                        desired_role=node.get("desired_role", ""),
                        busyness=node.get("busyness", ""),
                        contact_mail=node.get("contact_mail", ""),
                        contact_number=node.get("contact_number", ""),
                        work_place=node.get("work_place", ""),
                        work_position=node.get("work_position", ""),
                        city=node.get("city", ""),
                        portfolio=node.get("portfolio", ""),
                        about=node.get("about", ""),
                        status=ProfileStatusEnum(
                            node["status"]) if node.get("status") else None
                    )
                )

            return profiles

        async with self._driver.session() as session:
            profiles = await session.execute_read(tx_func)

        if len(profiles) != len(ids):
            found_ids = {p.id for p in profiles}
            missing_ids = {i for i in ids if i not in found_ids}
            raise adapter_errors.ProfileNotFoundError(
                f"Profiles with ids: {missing_ids} doesn't exist")

        return profiles

    async def update_profile(self, profile: Profile) -> None:
        '''
        Update profile parameters

        Args:
            profile (Profile): The profile data to update

        Raises:
            ProfileNotFoundError: If update non-existent profile
        '''
        async def tx_func(tx):
            result = await tx.run(
                UPDATE_PROFILE_QUERY,
                {
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

                    "status": profile.status.value if profile.status else None
                })

            record = await result.single()
            return record

        async with self._driver.session() as session:
            record = await session.execute_write(tx_func)

        if record is None:
            raise adapter_errors.ProfileNotFoundError(
                f"Given profile doesn't exist")
