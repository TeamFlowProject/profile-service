from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8")

    database_dsn: str = "postgresql://user:password@localhost:5432/track_db"
    kafka_bootstrap: str = "localhost:9092"
    keycloak_url: str = "localhost:8001"
    http_host: str = "0.0.0.0"
    http_port: int = 8000
    kafka_topic_commands: str = "profile-commands"
    kafka_topic_events: str = "profile-events"
    kafka_group_id: str = "profile-service"
    log_level: str = "DEBUG"
