from src.models.profile import Profile
from src.services.protocols import ProfileRepository, ProfileKafkaProducer, KeyCloak


class ProfileService:
    def __init__(self, profile_repository: ProfileRepository, kafka_producer: ProfileKafkaProducer, keycloak: KeyCloak) -> None:
        ...
