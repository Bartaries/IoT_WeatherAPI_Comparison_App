import logging
import os
from logging.handlers import RotatingFileHandler
from flask import app
from termcolor import colored


class ColoredFormatter(logging.Formatter):
    LEVEL_COLORS = {
        'DEBUG': 'cyan',
        'INFO': 'green',
        'WARNING': 'yellow',
        'ERROR': 'red',
        'CRITICAL': 'magenta',
    }

    def format(self, record):
        colored_record = logging.makeLogRecord(record.__dict__)

        level_name = colored_record.levelname
        color = self.LEVEL_COLORS.get(level_name, 'white')

        colored_record.levelname = colored(level_name, color, attrs=['bold'])

        return super().format(colored_record)
    
CUSTOM_FORMAT = (
    "%(asctime)s - [%(levelname)s] - %(name)s - "
    "[PID: %(process)d - Thread: %(thread)d] - "
    "[File: %(module)s.py, Line: %(lineno)d] - %(message)s"
)
formatter = logging.Formatter(CUSTOM_FORMAT)
stream_formatter = ColoredFormatter(CUSTOM_FORMAT)

log_dir = 'logs'
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

file_handler = RotatingFileHandler(
    os.path.join(log_dir, 'app.log'),
    maxBytes=1024 * 1024 * 10,
    backupCount=5
)
file_handler.setFormatter(formatter)

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(stream_formatter)

def setup_logging(app, level=logging.INFO):
    for handler in app.logger.handlers[:]:
        app.logger.removeHandler(handler)

    logger = app.logger
    logger.setLevel(level)

    if not logger.handlers:
        logger.addHandler(file_handler)
        logger.addHandler(stream_handler)

    logger.propagate = False