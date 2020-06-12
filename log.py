import logging
import sys

def get_logger(name : str):
    logger = logging.getLogger("[" + name + "]")
    logger.setLevel(logging.INFO)
    logger_handler = logging.StreamHandler(stream=sys.stdout)
    logger_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)-8s %(name)-8s %(message)s '))
    logger.addHandler(logger_handler)     
    return logger