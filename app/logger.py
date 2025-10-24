import logging
import sys
from datetime import datetime
import os


def setup_logger():
    """Настройка логгера с записью в файл и выводом в консоль"""

    if not os.path.exists('logs'):
        os.makedirs('logs')

    log_filename = f"logs/parser_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

    logger = logging.getLogger('wildberries_parser')
    logger.setLevel(logging.INFO)

    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    file_handler = logging.FileHandler(log_filename, encoding='utf-8')
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger

logger = setup_logger()