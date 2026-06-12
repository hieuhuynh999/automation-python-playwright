from pathlib import Path

from loguru import logger

Path("logs").mkdir(exist_ok=True)
logger.add("logs/automation.log", rotation="10 MB", retention="10 days", enqueue=True)
