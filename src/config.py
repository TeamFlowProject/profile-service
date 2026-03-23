from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8")

    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_auth: tuple = ("neo4j", "password")
    kafka_bootstrap: str = "localhost:9092"
    keycloak_url: str = "localhost:8001"
    keycloak_realm: str = "master"
    keycloak_client_id: str = "profile-service"
    keycloak_client_secret: str = ""
    http_host: str = "0.0.0.0"
    http_port: int = 8000
    kafka_topic_commands: str = "profile-commands"
    kafka_topic_events: str = "profile-events"
    kafka_group_id: str = "profile-service"
    log_level: str = "DEBUG"
