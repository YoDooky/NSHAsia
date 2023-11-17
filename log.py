import logging
import re

from selenium.common import WebDriverException

from config import LOG_FILE_PATH


def init_logging_config():
    log_file = f'{LOG_FILE_PATH}'
    try:
        with open(log_file, 'x') as f:
            f.write('')
    except FileExistsError:
        pass
    logging.basicConfig(filename=log_file,
                        filemode='a',
                        format='[%(asctime)s] %(message)s',
                        datefmt='%Y-%m-%d,%H:%M:%S',
                        level=logging.DEBUG)


def print_log(message: str = '', exception=None, silent: bool = False):
    if isinstance(exception, WebDriverException):
        exception.msg = exception.msg.split('(Session info:')[0]
        exception.stacktrace = {}

    if not silent:
        print(message)
    if message:
        logging.debug(message)
    if exception:
        logging.exception(exception)
