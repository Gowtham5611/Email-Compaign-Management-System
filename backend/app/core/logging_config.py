import os
import logging
from datetime import datetime
from app.core.config import settings

LOG_FILE = os.path.join(settings.LOG_DIR, "activity_log.txt")

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("email_sender")

def log_activity(message: str, level: str = "info") -> str:
    """
    Structured logger to write activity log and return formatted line.
    Preserves original log structure while integrating python logging.
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    formatted = f"[{timestamp}] {message}"
    
    if level.lower() == "error":
        logger.error(message)
    elif level.lower() == "warning":
        logger.warning(message)
    else:
        logger.info(message)

    return formatted

