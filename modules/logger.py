"""
logger.py
Provides a single shared logger instance so every module reports errors
and events consistently (Non-functional requirement: Logging & Monitoring).
"""

import logging
import config


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(getattr(logging, config.LOG_LEVEL, logging.INFO))

        file_handler = logging.FileHandler(config.LOG_FILE)
        console_handler = logging.StreamHandler()

        fmt = logging.Formatter(
            "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        file_handler.setFormatter(fmt)
        console_handler.setFormatter(fmt)

        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
    return logger
