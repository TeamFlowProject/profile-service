from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8")

    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_auth: tuple = ("neo4j", "password")

    keycloak_server_url: str = "http://localhost:8080/"
    keycloak_username: str = "admin"
    keycloak_password: str = "password"
    keycloak_realm_name: str = "master"
    keycloak_user_realm_name: str = "only_if_other_realm_than_master"
    
    kafka_bootstrap: str = "localhost:9092"
    http_host: str = "0.0.0.0"
    http_port: int = 8000
    kafka_topic_commands: str = "profile-commands"
    kafka_topic_events: str = "profile-events"
    kafka_group_id: str = "profile-service"
    log_level: str = "DEBUG"
