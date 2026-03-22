from src.models.profile import Profile
from src.services.protocols import ProfileRepository, ProfileKafkaProducer


class ProfileService:
    def __init__(self, profile_repository: ProfileRepository, kafka_producer: ProfileKafkaProducer) -> None:
        ...
