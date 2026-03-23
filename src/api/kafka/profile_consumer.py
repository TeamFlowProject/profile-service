from aiokafka import AIOKafkaConsumer
from src.services.profile_service import ProfileService


class ProfileKafkaConsumer:
    def __init__(self, consumer: AIOKafkaConsumer, profile_service: ProfileService) -> None:
        ...

    async def start(self) -> None:
        ...
