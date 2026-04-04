import asyncio

import typer
import uvicorn
import sys
from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
from fastapi import FastAPI
from loguru import logger
from neo4j import AsyncGraphDatabase
from keycloak import KeycloakAdmin

from src.adapters.clients.kafka_producer import KafkaProducerClient
from src.adapters.clients.keycloak import KeycloakClient
from src.adapters.repository.profile_repository import ProfileNeo4jRepository
from src.api.http.profile_router import create_profile_router
from src.api.kafka.profile_consumer import ProfileKafkaConsumer
from src.services.profile_service import ProfileService
from src.config import Settings


async def _run(settings: Settings) -> None:
    # Connecting database interconnection implementation with Duck Typing
    logger.debug("Connecting to database: {}", settings.neo4j_uri)
    db_connection = AsyncGraphDatabase.driver(
        settings.neo4j_uri, auth=settings.neo4j_auth
    )
    profile_repository = ProfileNeo4jRepository(db_connection)
    logger.debug("Database connection established")

    admin = KeycloakAdmin(
        server_url=settings.keycloak_server_url,
        username=settings.keycloak_username,
        password=settings.keycloak_password,
        realm_name=settings.keycloak_realm_name,
        user_realm_name=settings.keycloak_user_realm_name,
    )
    keycloak = KeycloakClient(admin)
    logger.debug("Keycloak client created {}", settings.keycloak_server_url)

    # Starting Kafka producer
    logger.debug("Starting Kafka producer: {}", settings.kafka_bootstrap)
    producer = AIOKafkaProducer(bootstrap_servers=settings.kafka_bootstrap)
    await producer.start()
    kafka_producer = KafkaProducerClient(producer)
    logger.debug("Kafka producer started")

    # Starting service itself with prepared submodules
    profile_service = ProfileService(profile_repository, kafka_producer, keycloak)
    logger.debug("Profile Service started")

    # Start Fastapi app and make it able to use all endpoints
    fastapi_app = FastAPI(title="Profile Service")
    router = create_profile_router(profile_service)
    fastapi_app.include_router(router)
    logger.debug("HTTP router registered")

    # Create kafka consumer to receive messages from other services
    consumer = AIOKafkaConsumer(
        settings.kafka_topic_commands,
        bootstrap_servers=settings.kafka_bootstrap,
        group_id=settings.kafka_group_id,
    )
    kafka_consumer = ProfileKafkaConsumer(consumer, profile_service)
    logger.debug(
        "Kafka consumer created: topic={}, group={}",
        settings.kafka_topic_commands,
        settings.kafka_group_id,
    )

    # Starting service of assembled app with prepared parameters using uvicorn
    config = uvicorn.Config(
        fastapi_app, host=settings.http_host, port=settings.http_port
    )
    server = uvicorn.Server(config)
    logger.info("Starting service on {}:{}", settings.http_host, settings.http_port)

    try:
        await asyncio.gather(server.serve(), kafka_consumer.start())
    finally:
        logger.debug("Shutting down")
        await producer.stop()
        await db_connection.close()
        logger.info("Shutdown complete")


app = typer.Typer()


def _setup_logger(settings: Settings) -> None:
    logger.remove()
    logger.add(
        sink=sys.stderr,
        level=settings.log_level.upper(),
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level:<8}</level> | <cyan>{name}</cyan>:<cyan>{line}</cyan> - {message}",
    )


@app.command()
def run() -> None:
    settings = Settings()
    _setup_logger(settings)
    logger.debug("Settings loaded: {}", settings.model_dump())
    asyncio.run(_run(settings))


@app.command()
def migrate() -> None:
    settings = Settings()
    _setup_logger(settings)
    logger.info("Running migration...")


if __name__ == "__main__":
    app()
