"""Módulo principal da aplicação."""
import asyncio
import logging
import sys
import discord

from src.containers import Container
from src.infra.logging.setup import setup_logging

logger = logging.getLogger(__name__)


class Application:
    """Gerencia o ciclo de vida da aplicação."""

    def __init__(self):
        """Inicializa a aplicação."""
        self.container = Container()
        self.container.wire(
            modules=[
                sys.modules[__name__],
                "src.presentation.discord.cogs.admin",
                "src.presentation.discord.cogs.config",
                "src.presentation.discord.cogs.info",
                "src.presentation.discord.cogs.roles",
                "src.presentation.discord.bot",
                "src.infra.web_scraper.uepa_scraper",
            ]
        )

    def setup(self):
        """Configura a aplicação."""
        setup_logging(
            level=self.container.config.LOG_LEVEL(),
            env=self.container.config.ENVIRONMENT(),
        )

        db = self.container.db_connection()
        db.setup()

    async def start(self):
        """Inicia a aplicação."""
        self.setup()
        bot = self.container.bot()

        try:
            logger.info("Iniciando o bot...")
            await bot.start(self.container.config.DISCORD_TOKEN())
        except discord.errors.LoginFailure:
            logger.critical("Token do Discord inválido.")
        except KeyboardInterrupt:
            logger.info("Bot desligado pelo usuário.")
        except Exception as e:
            logger.critical("Erro fatal ao iniciar o bot: %s", e, exc_info=True)
        finally:
            if not bot.is_closed():
                await bot.close()
            logger.info("Bot desligado.")


if __name__ == "__main__":
    app = Application()
    asyncio.run(app.start())
