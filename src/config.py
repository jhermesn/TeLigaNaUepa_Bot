"""Carrega e valida as configurações do ambiente."""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Carrega e valida as configurações do ambiente."""

    DISCORD_TOKEN: str = ""
    CHECK_INTERVAL_MINUTES: int = 5
    LOG_LEVEL: str = "INFO"
    DATABASE_URL: str = "sqlite:///data/uepa_bot.db"
    UEPA_EDITAIS_URL: str = "https://www.uepa.br/pt-br/editais"
    ENVIRONMENT: str = "development"
    TZ: str = "America/Sao_Paulo"

    class Config:
        """Configurações do Pydantic."""

        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
