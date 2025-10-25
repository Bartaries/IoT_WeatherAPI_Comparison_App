import logging
import os
from logging.handlers import RotatingFileHandler
from flask import app
from termcolor import colored
    
CUSTOM_FORMAT = (
    "%(asctime)s - [%(levelname)s] - %(name)s - "
    "[PID: %(process)d - Thread: %(thread)d] - "
    "[File: %(module)s.py, Line: %(lineno)d] - %(message)s"
)
formatter = logging.Formatter(CUSTOM_FORMAT)

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
stream_handler.setFormatter(formatter)

def setup_logging(app, level=logging.INFO):
    logger = app.logger
    logger.setLevel(level)

    if not logger.handlers:
        logger.addHandler(file_handler)
        logger.addHandler(stream_handler)