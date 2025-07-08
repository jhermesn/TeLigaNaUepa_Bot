import os
from typing import Optional
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass
class Settings:
    """Carrega e valida as configurações do ambiente."""

    # Discord Bot
    DISCORD_TOKEN: str = os.getenv("DISCORD_TOKEN", "")

    # Bot Settings
    CHECK_INTERVAL_MINUTES: int = int(os.getenv("CHECK_INTERVAL_MINUTES", "5"))
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO").upper()

    # Database
    DATABASE_FILE: str = os.getenv("DATABASE_FILE", "data/uepa_bot.db")

    # UEPA Website
    UEPA_EDITAIS_URL: str = os.getenv("UEPA_EDITAIS_URL", "https://www.uepa.br/pt-br/editais")

    # Environment
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    TZ: str = os.getenv("TZ", "America/Sao_Paulo")

    def __post_init__(self):
        """Valida as configurações após a inicialização."""
        if not self.DISCORD_TOKEN:
            raise ValueError("DISCORD_TOKEN não foi configurado nas variáveis de ambiente.")


# Criar instância com validação automática
settings = Settings() 