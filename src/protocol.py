from autobahn.asyncio.websocket import WebSocketServerProtocol
from log import logger
from log import log_exceptions
from player import Player

import json


# Player STATUS
STARTING = 0
AWAITING = 1
ACTIVE = 2
ENDED = 3


class Protocol(WebSocketServerProtocol):

    PLAYER_STATUS = STARTING

    # Events
    @log_exceptions
    def onConnect(self, request):
        logger.info(f'CLIENT: {request.peer} ==> Connecting')

    @log_exceptions
    def onOpen(self):
        logger.info(f'CLIENT: {self.peer} ==> Opened')
        self.open_client()

    @log_exceptions
    def onClose(self, wasClean, code, reason):
        logger.info(f'CLIENT: {self.peer} ==> Closed')
        self.close_client()

    @log_exceptions
    def onMessage(self, payload, isBinary):
        try:
            logger.info(f'CLIENT: {self.peer} ==> Socket message')
            payload = json.loads(payload.decode('utf8'))
            self.process_message(payload)
        except ValueError:
            response = {
                'action': 'ERROR',
                'reason': 'The message must be JSON',
            }
            logger.warning(f'CLIENT: {self.peer} ==> Socket message error')
            self.sendMessage(json.dumps(response).encode('utf-8'))

    # Logic
    def change_player_status(self, status):
        self.PLAYER_STATUS = status

    def open_client(self):
        self.player = Player(index = self.factory.num_clients + 1)
        self.send_client_info()
        self.factory.register_client(self)

    def close_client(self):
        self.factory.unregister_client(self)

    def send_client_info(self):
        response = {
            'action': 'PLAYER_INFO',
            'uid': self.player.UID,
            'name': self.player.name,
            'colour': self.player.colour,
            'gender': self.player.gender,
        }
        self.sendMessage(json.dumps(response).encode('utf-8'))

    def process_message(self, payload):
        switcher = {
            'MESSAGE': self.chat_message_action,
            'UPDATE_PLAYER': self.update_player_action,
        }
        action = switcher.get(payload.get('action', False), self.default_action)
        action(payload)

    def default_action(self, payload):
        logger.warning(f'CLIENT: {self.peer} ==> Unknown or missing action')
        response = {
            'action': 'ERROR',
            'reason': 'Unknown action',
        }
        self.sendMessage(json.dumps(response).encode('utf-8'))

    def chat_message_action(self, payload):
        logger.info(f'CLIENT: {self.peer} ==> Chat message')
        message = payload['message']
        self.send_message(message)

    def send_message(self, message):
        response = {
            'action': 'MESSAGE',
            'message': message,
            'name': self.player.name,
            'colour': self.player.colour,
            'gender': self.player.gender,
        }
        self.factory.broadcast(json.dumps(response).encode('utf-8'))

    def update_player_action(self, payload):
        logger.info(f'CLIENT: {self.peer} ==> Updated')

        name = payload['name'] or self.player.name
        colour = payload['colour']
        gender = payload['gender']

        previous_name = self.player.name
        previous_colour = self.player.colour
        previous_gender = self.player.gender

        self.player.name = name
        self.player.colour = colour
        self.player.gender = gender

        current_info = {
            'name': name,
            'colour': colour,
            'gender': gender,
        }
        previous_info = {
            'name': previous_name,
            'colour': previous_colour,
            'gender': previous_gender,
        }

        self.send_updated_player(previous_info, current_info)

    def send_updated_player(self, previous_info, current_info):
        response = {
            'action': 'PLAYER_UPDATED',
            'previous': previous_info,
            'current': current_info,
        }
        self.factory.broadcast(json.dumps(response).encode('utf-8'))
