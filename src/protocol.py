from autobahn.asyncio.websocket import WebSocketServerProtocol
from log import logger

import json


class Protocol(WebSocketServerProtocol):

    def onConnect(self, request):
         logger.info(f'CLIENT: {request.peer} ==> Connecting')

    def onOpen(self):
        logger.info(f'CLIENT: {self.peer} ==> Opened')
        self.factory.register_client(self)

    def onClose(self, wasClean, code, reason):
        logger.info(f'CLIENT: {self.peer} ==> Closed')
        self.factory.unregister_client(self)

    def onMessage(self, payload, isBinary):
        try:
            logger.info(f'CLIENT: {self.peer} ==> Socket message')
            payload = json.loads(payload.decode('utf8'))
            print(payload)
            self.process_message(payload)
        except ValueError:
            response = {
                'status': 'error',
                'reason': 'The message must be JSON',
            }
            logger.warning(f'CLIENT: {self.peer} ==> Socket message error')
            self.sendMessage(json.dumps(response).encode('utf-8'))

    def process_message(self, payload):
        switcher = {
            'MESSAGE': self.chat_message_action,
            'LOGIN': self.login_action,
        }
        action = switcher.get(payload.get('action', False), self.default_action)
        action(payload)

    def default_action(self, payload):
        logger.warning(f'CLIENT: {self.peer} ==> Unknown or missing action')
        response = {
            'status': 'error',
            'reason': 'Unknown action',
        }
        self.sendMessage(json.dumps(response).encode('utf-8'))

    def chat_message_action(self, payload):
        logger.info(f'CLIENT: {self.peer} ==> Chat message')
        message = payload['message']
        sender = self.peer
        self.factory.send_message(message, sender)

    def login_action(self, payload):
        pass
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

