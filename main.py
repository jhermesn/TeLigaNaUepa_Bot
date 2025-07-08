import asyncio
import aiohttp
import logging
import os

from src.config import settings
from src.infra.logging.setup import setup_logging
from src.infra.database.connection import setup_database
from src.infra.web_scraper.uepa_scraper import UepaScraper
from src.presentation.discord.bot import UEPABot

# Repositórios
from src.infra.database.repositories.all_editais_repository import AllEditaisRepository
from src.infra.database.repositories.role_repository import RoleRepository
from src.infra.database.repositories.guild_settings_repository import GuildSettingsRepository
from src.infra.database.repositories.log_repository import LogRepository

# Garante que os diretórios necessários existam
os.makedirs("logs", exist_ok=True)
os.makedirs("data", exist_ok=True)

# Configura o logging
logger = setup_logging()

async def main():
    """Ponto de entrada principal para iniciar o bot."""
    # Setup do banco de dados
    setup_database()

    async with aiohttp.ClientSession() as session:
        # Injeção de dependência
        # Camada de Infraestrutura
        scraper = UepaScraper(session)
        all_editais_repo = AllEditaisRepository()
        role_repo = RoleRepository()
        guild_repo = GuildSettingsRepository()
        log_repo = LogRepository()

        # Camada de Apresentação
        bot = UEPABot(
            guild_repo=guild_repo,
            all_editais_repo=all_editais_repo,
            role_repo=role_repo,
            log_repo=log_repo,
            scraper=scraper,
        )

        try:
            logger.info("Iniciando o bot...")
            await bot.start(settings.DISCORD_TOKEN)
        except Exception as e:
            logger.critical(f"Erro fatal ao iniciar o bot: {e}", exc_info=True)
        finally:
            if not bot.is_closed():
                await bot.close()
            logger.info("Bot desligado.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot desligado pelo usuário.")
    except Exception as e:
        logger.error(f"Erro inesperado no loop principal: {e}", exc_info=True)