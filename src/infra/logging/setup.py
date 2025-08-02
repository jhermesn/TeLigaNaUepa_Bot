"""Configura o sistema de logging para o bot."""

import logging
import sys
import os


class SingleLevelFilter(logging.Filter):
    """Filtro para logging de um nível específico."""
    def __init__(self, level):
        super().__init__()
        self.level = level

    def filter(self, record):
        return record.levelno == self.level


def setup_logging(level: str = "INFO", env: str = "development"):
    """Configura o sistema de logging para o bot."""
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    formatter = logging.Formatter(log_format)

    # Create directories
    if not os.path.exists("logs/info"):
        os.makedirs("logs/info")
    if not os.path.exists("logs/error"):
        os.makedirs("logs/error")

    # Handlers
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(formatter)

    info_file_handler = logging.FileHandler("logs/info/info.log")
    info_file_handler.setLevel(logging.INFO)
    info_file_handler.addFilter(SingleLevelFilter(logging.INFO))
    info_file_handler.setFormatter(formatter)

    error_file_handler = logging.FileHandler("logs/error/error.log")
    error_file_handler.setLevel(logging.ERROR)
    error_file_handler.setFormatter(formatter)
    
    handlers = [stream_handler, info_file_handler, error_file_handler]

    if env == "production":
        prod_file_handler = logging.FileHandler("logs/uepa_bot.log")
        prod_file_handler.setFormatter(formatter)
        handlers.append(prod_file_handler)

    logging.basicConfig(
        level=level,
        format=log_format,
        handlers=handlers,
    )

    logger = logging.getLogger("UEPABot")
    logger.info("Sistema de logging configurado para o nível %s.", level)
    return logger
