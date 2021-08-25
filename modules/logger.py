# ORIGINAL: https://github.com/splunk/attack_range_local/
import logging


def setup_logging(log_path, log_level):
    """Creates a shared logging object for the application"""

    # create logging object
    logger = logging.getLogger('attack_lab')
    logger.setLevel(log_level)
    # create a file and console handler
    fh = logging.FileHandler(log_path)
    fh.setLevel(log_level)
    ch = logging.StreamHandler()
    ch.setLevel(log_level)
    # create a logging format
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(message)s')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    # add the handlers to the logger
    logger.addHandler(fh)
    logger.addHandler(ch)
    return logger


def get():
    logger = logging.getLogger('attack_lab')
    return logger
