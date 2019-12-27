from autobahn.asyncio.websocket import WebSocketServerProtocol

import json
import logging

logger = logging.getLogger('monopoly.server')


class Protocol(WebSocketServerProtocol):

    def onConnect(self, request):
        print('Client connecting: {0}'.format(request.peer))
        logger.warning('TEST2')

    def onOpen(self):
        print("WebSocket connection open.")
        self.factory.register_client(self)

    def onMessage(self, payload, isBinary):
        try:
            payload = json.loads(payload.decode('utf8'))
            self.process_message(payload)
        except ValueError:
            response = {
                'status': 'error',
                'reason': 'The message must be JSON',
            }
            self.sendMessage(json.dumps(response).encode('utf-8'))

        # if action == 'ADD_PLAYER':
        #     data = json.loads(payload[1])
        #     self.factory.add_player(data, self)

        # if action == 'MESSAGE':
        #     msg = "{} from {}".format(payload[1], self.peer)
        #     self.factory.send_message(msg)

        # payload = payload.decode('utf-8')
        # print('Message received: {0}'.format(payload))
        # if payload == 'UPDATE_CREDIT':
        #     self.monopoly.credit += 100
        # if payload == 'CLEAR_CREDIT':
        #     self.monopoly.credit = 0
        # self.sendMessage(str(self.monopoly.credit).encode('utf-8'), isBinary)

    def onClose(self, wasClean, code, reason):
        print("WebSocket connection closed: {0}".format(reason))
        self.factory.unregister_client(self)