import logging
import os
from pathlib import Path

class Logger:
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(self._get_log_level())

        if not self.logger.handlers:

            console_handler = logging.StreamHandler()
            console_handler.setFormatter(self._get_formatter())

            log_dir = Path("logs")
            log_dir.mkdir(exist_ok=True)
            file_handler = logging.FileHandler(log_dir / f"{name}.log", encoding="utf-8")
            file_handler.setFormatter(self._get_formatter())

            self.logger.addHandler(console_handler)
            self.logger.addHandler(file_handler)

    def _get_log_level(self) -> int:
        """Get logging level from env or default to DEBUG"""
        level_str = os.getenv("LOG_LEVEL", "DEBUG").upper()
        return getattr(logging, level_str, logging.DEBUG)

    def _get_formatter(self) -> logging.Formatter:
        return logging.Formatter(
            fmt="%(levelname)s | %(message)s | %(name)s | %(asctime)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )

    def get_logger(self) -> logging.Logger:
        return self.logger
