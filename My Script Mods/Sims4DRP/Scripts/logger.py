# logger.py
import logging
import os

def setup_logger():
    logger = logging.getLogger('my_logger')
    logger.setLevel(logging.INFO)
    log_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, 'discordRPC.log')
    file_handler = logging.FileHandler(log_file, mode='w')
    formatter = logging.Formatter('[%(asctime)s] %(levelname)s - %(message)s', datefmt='%H:%M:%S')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    return logger

logger = setup_logger()
