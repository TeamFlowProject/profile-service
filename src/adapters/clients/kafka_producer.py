from aiokafka import AIOKafkaProducer
from src.models.profile import Profile


class KafkaProducerClient:
    def __init__(self, producer: AIOKafkaProducer) -> None:
        ...
