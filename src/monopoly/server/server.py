from contextlib import suppress
from monopoly.server.log import logger
from monopoly.server.protocol import Protocol
from monopoly.server.factory import Factory

import asyncio
import signal


PORT = 9000
TRUST_X_FORWARDED_FOR = 1


def process_signal(signal_number, frame):
    raise SystemExit('Exiting')


def run_server():
    logger.info('SERVER: Starting')
    signal.signal(signal.SIGTERM, process_signal)

    factory = Factory()
    factory.protocol = Protocol
    factory.setProtocolOptions(trustXForwardedFor=TRUST_X_FORWARDED_FOR)

    try:
        loop = asyncio.get_event_loop()
        coro = loop.create_server(factory, '0.0.0.0', PORT)
        server = loop.run_until_complete(coro)
    except OSError as exception:
        logger.error('SERVER: Could not start')
        if exception.errno == 98:
            logger.error(f'SERVER: The port {PORT} is already in use')
            return 0
        else:
            raise exception

    try:
        logger.info('SERVER: Running')
        loop.run_forever()
    except KeyboardInterrupt:
        logger.info('SERVER: Shutting down by KeyboardInterrupt')
    except SystemExit:
        logger.info('SERVER: Shutting down by SystemExit')
    finally:
        logger.info('SERVER: Closing pending tasks')
        pending_tasks = asyncio.all_tasks(loop=loop)
        for task in pending_tasks:
            task.cancel()
            with suppress(asyncio.CancelledError):
                loop.run_until_complete(task)

        server.close()
        loop.close()
        logger.info('SERVER: Closed')
