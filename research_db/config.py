from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+psycopg://ananta:ananta@localhost:5432/ananta_research"
    ingestion_enabled: bool = False


settings = Settings()
