import logging
import os
import sys


def initiate_logger(logger_tittle: str):
    logger = logging.getLogger(logger_tittle)
    return logger


def print_exception(logger, e):
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    logger.error(
        f"Se produjo error en el archivo {fname}, con el siguiente texto: {e}, en la linea {exc_tb.tb_lineno}")
