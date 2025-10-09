import logging
import os
from datetime import datetime
from colorlog import ColoredFormatter

LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

log_filename = os.path.join(LOG_DIR, f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")

CONSOLE_LOG_FORMAT = "%(log_color)s[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s"
FILE_LOG_FORMAT = "[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

color_formatter = ColoredFormatter(
    CONSOLE_LOG_FORMAT,
    datefmt=DATE_FORMAT,
    log_colors={
        'DEBUG': 'cyan',
        'INFO': 'green',
        'WARNING': 'yellow',
        'ERROR': 'red',
        'CRITICAL': 'bold_red',
    }
)

file_formatter = logging.Formatter(FILE_LOG_FORMAT, DATE_FORMAT)

file_handler = logging.FileHandler(log_filename, encoding="utf-8")
file_handler.setFormatter(file_formatter)

console_handler = logging.StreamHandler()
console_handler.setFormatter(color_formatter)

logging.basicConfig(
    level=logging.INFO,
    handlers=[file_handler, console_handler]
)

def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)