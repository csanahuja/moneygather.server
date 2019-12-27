import logging


logger = logging.getLogger('monopoly.server')
logger.setLevel(logging.DEBUG)

handler_stream = logging.StreamHandler()
handler_file = logging.FileHandler('file.log')
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
