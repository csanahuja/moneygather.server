from log import logger
from protocol import Protocol
from factory import Factory

import asyncio
import signal


PORT = 9000


def process_signal(signal_number, frame):
    raise SystemExit('Exiting')


def start_server():
    logger.info('Starting the server')
    signal.signal(signal.SIGTERM, process_signal)

    factory = Factory()
    factory.protocol = Protocol

    try:
        loop = asyncio.get_event_loop()
        coro = loop.create_server(factory, '0.0.0.0', PORT)
        server = loop.run_until_complete(coro)
    except OSError as exc:
        logger.error('Could not start the server')
        if exc.errno == 98:
            logger.error(f'The port {PORT} is already in use')
            return 0
        else:
            raise exc

    try:
        logger.info('Server running')
        loop.run_forever()
    except KeyboardInterrupt:
        logger.info('Server closed by KeyboardInterrupt')
    except SystemExit:
        logger.info('Server closed by SystemExit')
    finally:
        server.close()
        loop.close()


if __name__ == '__main__':
    start_server()
