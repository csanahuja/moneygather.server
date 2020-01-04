"""
Module: log
"""
import functools
import logging
import sys


logger = logging.getLogger('moneygather.server')
logger.setLevel(logging.DEBUG)

handler_stream = logging.StreamHandler()
handler_file = logging.FileHandler(
    '/opt/Moneygather/moneygather.server/logs/server.log')
handler_stream.setLevel(logging.DEBUG)
handler_file.setLevel(logging.DEBUG)

formatter = logging.Formatter(
    '%(asctime)s - %(levelname)s - %(name)s - %(message)s',
    '%Y-%m-%d %H:%M:%S',
)
handler_stream.setFormatter(formatter)
handler_file.setFormatter(formatter)

logger.addHandler(handler_stream)
logger.addHandler(handler_file)


def handle_exception(exc_type, exc_value, exc_traceback):
    logger.error(
        "EXCEPTION:",
        exc_info=(exc_type, exc_value, exc_traceback),
    )


sys.excepthook = handle_exception


def log_exceptions(func):
    """ Logs uncaught exceptions to the logger
    """
    @functools.wraps(func)
    def wrapper_log_exceptions(*args, **kw):
        try:
            value = func(*args, **kw)
        except Exception:
            handle_exception(*sys.exc_info())
        else:
            return value
    return wrapper_log_exceptions
