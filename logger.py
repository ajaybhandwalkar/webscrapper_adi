import os
import sys
import logging
from pythonjsonlogger import jsonlogger


def init_logger():
    log_level = os.getenv('LOGLEVEL', 'info').upper()
    # format_str = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    format_str = "%(asctime)s [%(levelname)s] %(name)s - %(funcName)s: %(message)s"
    format_str = "%(asctime)s [%(levelname)s] %(filename)s - %(funcName)s: %(message)s"
    formatter = logging.Formatter(format_str)
    log = logging.getLogger('webscraper')
    if not log.hasHandlers():
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        log.addHandler(console_handler)
        log.setLevel(log_level)
    return log


if __name__ == '__main__':
    logger = init_logger()
    logger.info("info")
    logger.error("error")
    logger.warning("warning")
