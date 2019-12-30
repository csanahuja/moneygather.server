from autobahn.asyncio.websocket import WebSocketServerProtocol
from log import logger
from log import log_exceptions
from player import Player

import json
import random


# Player STATUS
NOT_READY = 0
READY = 1


class Protocol(WebSocketServerProtocol):

    PLAYER_STATUS = NOT_READY

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
        logger.info(f'CLIENT: {self.peer} ==> Closed: Code {code} Reason: {reason}')
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
    @property
    def status(self):
        return self.PLAYER_STATUS

    @status.setter
    def status(self, value):
        self.PLAYER_STATUS = value

    def change_player_status(self, status):
        self.status = status

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
            'PLAYER_UPDATED': self.player_updated_action,
            'PLAYER_STATUS': self.player_status_action,
            'THROW_DICES': self.throw_dices_action,
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

    def player_updated_action(self, payload):
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

        self.send_player_updated(previous_info, current_info)

    def send_player_updated(self, previous_info, current_info):
        response = {
            'action': 'PLAYER_UPDATED',
            'previous': previous_info,
            'current': current_info,
        }
        self.factory.broadcast(json.dumps(response).encode('utf-8'))

    def player_status_action(self, payload):
        logger.info(f'CLIENT: {self.peer} ==> Changed status to: {payload["status"]}')
        if payload['status'] == 'ready':
            self.change_player_status(READY)
            self.send_player_status('ready')
            self.factory.client_is_ready()
        else:
            self.change_player_status(NOT_READY)
            self.send_player_status('not_ready')
            self.factory.client_is_not_ready()

    def send_player_status(self, status):
        response = {
            'action': 'PLAYER_STATUS',
            'status': status,
            'name': self.player.name,
            'colour': self.player.colour,
            'gender': self.player.gender,
        }
        self.factory.broadcast(json.dumps(response).encode('utf-8'))

    def throw_dices_action(self, payload):
        logger.info(f'CLIENT: {self.peer} ==> Throwed dices')
        response = {
            'action': 'DICES_RESULT',
            'dice1': self.number_to_string(random.randint(1, 6)),
            'dice2': self.number_to_string(random.randint(1, 6)),
        }
        self.sendMessage(json.dumps(response).encode('utf-8'))

    def number_to_string(self, number):
        num_to_string_dict = {
            1: 'one',
            2: 'two',
            3: 'three',
            4: 'four',
            5: 'five',
            6: 'six',
        }
        return num_to_string_dict[number]
