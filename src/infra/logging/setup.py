import logging
import os
import sys

from src.config import settings


def setup_logging():
    """Configura o sistema de logging para o bot."""
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    handlers = [logging.StreamHandler(sys.stdout)]

    if settings.ENVIRONMENT == "production":
        handlers.append(logging.FileHandler("logs/uepa_bot.log"))

    logging.basicConfig(
        level=settings.LOG_LEVEL,
        format=log_format,
        handlers=handlers,
    )

    logger = logging.getLogger("UEPABot")
    logger.info("Sistema de logging configurado.")
    return logger 