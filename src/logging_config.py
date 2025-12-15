"""Logging configuration with rotating file & optional console handlers."""
from __future__ import annotations

import logging
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path

_INITIALIZED = False


def init_logging(name: str = "shoplifting_app") -> logging.Logger:
    """Initialize logging once and return an application logger.

    Env vars:
      SD_LOG_LEVEL   -> logging level (default INFO)
      SD_LOG_DIR     -> directory for log files (default logs/)
      SD_LOG_FILE    -> filename (default app.log)
      SD_LOG_CONSOLE -> '1' to enable console handler (default '1')
    """
    global _INITIALIZED
    logger = logging.getLogger(name)
    if _INITIALIZED:
        return logger

    level_name = os.getenv("SD_LOG_LEVEL", "INFO").upper()
    level = getattr(logging, level_name, logging.INFO)
    logger.setLevel(level)

    log_dir = Path(os.getenv("SD_LOG_DIR", "logs"))
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / os.getenv("SD_LOG_FILE", "app.log")

    fmt = logging.Formatter(
        fmt="%(asctime)s | %(levelname)s | %(threadName)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Rotating file handler
    try:
        fh = RotatingFileHandler(str(log_file), maxBytes=1_000_000, backupCount=5, encoding="utf-8")
        fh.setLevel(level)
        fh.setFormatter(fmt)
        logger.addHandler(fh)
    except Exception as e:
        logging.getLogger(__name__).warning("init_logging: failed file handler: %s", e)

    # Console handler (optional)
    if os.getenv("SD_LOG_CONSOLE", "1") == "1":
        ch = logging.StreamHandler()
        ch.setLevel(level)
        ch.setFormatter(logging.Formatter("%(levelname)s | %(name)s | %(message)s"))
        logger.addHandler(ch)

    # Avoid duplicate logs bubbling to root
    logger.propagate = False

    _INITIALIZED = True
    logger.debug("Logging initialized level=%s file=%s", level_name, log_file)
    return logger
