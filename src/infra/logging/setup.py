"""Configura o sistema de logging para o bot."""

import logging
import sys


def setup_logging(level: str = "INFO", env: str = "development"):
    """Configura o sistema de logging para o bot."""
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    handlers = [logging.StreamHandler(sys.stdout)]

    if env == "production":
        handlers.append(logging.FileHandler("logs/uepa_bot.log"))

    logging.basicConfig(
        level=level,
        format=log_format,
        handlers=handlers,
    )

    logger = logging.getLogger("UEPABot")
    logger.info("Sistema de logging configurado para o nível %s.", level)
    return logger
