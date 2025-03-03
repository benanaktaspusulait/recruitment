import logging
import sys
from pathlib import Path
from loguru import logger
from datetime import datetime

def setup_logging():
    # Create logs directory if it doesn't exist
    LOGS_DIR = Path("logs")
    LOGS_DIR.mkdir(exist_ok=True)

    # Remove default logger
    logger.remove()

    # Configure loguru logger
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level="INFO"
    )
    
    logger.add(
        LOGS_DIR / f"app_{datetime.now().strftime('%Y%m%d')}.log",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level="DEBUG",
        rotation="00:00",  # Create new file at midnight
        retention="30 days",  # Keep logs for 30 days
    )

    # Create a class to convert loguru logger to standard logging
    class InterceptHandler(logging.Handler):
        def emit(self, record):
            # Get corresponding Loguru level if it exists
            try:
                level = logger.level(record.levelname).name
            except ValueError:
                level = record.levelno

            # Find caller from where originated the logged message
            frame, depth = logging.currentframe(), 2
            while frame.f_code.co_filename == logging.__file__:
                frame = frame.f_back
                depth += 1

            logger.opt(depth=depth, exception=record.exc_info).log(
                level, record.getMessage()
            )

    # Configure standard logging to use loguru
    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)
    
    return logger 