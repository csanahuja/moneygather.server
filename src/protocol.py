from autobahn.asyncio.websocket import WebSocketServerProtocol
from log import logger
from player import Player

import json


# Client STATUS
AWAITING_TURN = 0
ACTIVE_TURN = 1


class Protocol(WebSocketServerProtocol):

    def onConnect(self, request):
         logger.info(f'CLIENT: {request.peer} ==> Connecting')

    def onOpen(self):
        logger.info(f'CLIENT: {self.peer} ==> Opened')
        self.open_client()

    def onClose(self, wasClean, code, reason):
        logger.info(f'CLIENT: {self.peer} ==> Closed')
        self.close_client()

    def onMessage(self, payload, isBinary):
        try:
            logger.info(f'CLIENT: {self.peer} ==> Socket message')
            payload = json.loads(payload.decode('utf8'))
            self.process_message(payload)
        except ValueError:
            response = {
                'status': 'error',
                'reason': 'The message must be JSON',
            }
            logger.warning(f'CLIENT: {self.peer} ==> Socket message error')
            self.sendMessage(json.dumps(response).encode('utf-8'))

    def open_client(self):
        self.factory.register_client(self)
        self.client_status = AWAITING_TURN
        self.player = Player(index = self.factory.num_players)
        self.send_client_info()
        self.send_player_action(self.player.name, 'PLAYER_CONNECTED')

    def close_client(self):
        self.factory.unregister_client(self)
        self.send_player_action(self.player.name, 'PLAYER_DISCONNECTED')

    def send_player_action(self, name, action):
        response = {
            'action': action,
            'status': 'ok',
            'name': self.player.name,
            'colour': self.player.colour,
            'gender': self.player.gender,
        }
        self.factory.broadcast(json.dumps(response).encode('utf-8'))

    def send_client_info(self):
        response = {
            'action': 'PLAYER_INFO',
            'status': 'ok',
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
            'status': 'error',
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
            'status': 'ok',
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
            'status': 'ok',
            'previous': previous_info,
            'current': current_info,
        }
        self.factory.broadcast(json.dumps(response).encode('utf-8'))
