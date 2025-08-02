"""Módulo principal da aplicação."""
import asyncio
import logging
import sys
import glob
import os
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
        
        log_files = glob.glob("logs/**/*.log", recursive=True)
        for log_file in log_files:
            if os.path.exists(log_file):
                try:
                    with open(log_file, "w") as f:
                        f.truncate(0)
                    print(f"Arquivo de log limpo: {log_file}")
                except IOError as e:
                    print(f"Erro ao limpar o arquivo de log {log_file}: {e}")

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
        bot.container = self.container

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
