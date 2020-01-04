from autobahn.asyncio.websocket import WebSocketServerProtocol
from moneygather.server.log import logger
from moneygather.server.log import log_exceptions

import json
import random


class Protocol(WebSocketServerProtocol):

    @log_exceptions
    def onConnect(self, request):
        self.logger('info', 'Connecting')

    @log_exceptions
    def onOpen(self):
        self.logger('info', 'Opened')
        self.factory.register_client(self)

    @log_exceptions
    def onClose(self, wasClean, code, reason):
        self.logger('info', f'Closed: Code {code} Reason: {reason}')
        self.factory.unregister_client(self)

    @log_exceptions
    def onMessage(self, payload, isBinary):
        try:
            self.logger('info', 'Socket message')
            payload = json.loads(payload.decode('utf8'))
            self.process_message(payload)
        except ValueError:
            response = {
                'action': 'ERROR',
                'reason': 'The message must be JSON',
            }
            self.logger('warning', 'Socket message error')
            self.sendMessage(json.dumps(response).encode('utf-8'))

    def logger(self, method, message):
        pre_message = f'CLIENT: {self.peer} ==>'

        if method == 'info':
            logger.info(f'{pre_message} {message}')
        if method == 'warning':
            logger.warning(f'{pre_message} {message}')

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
        action = payload.get('action', False)
        action_method = switcher.get(action, self.default_action)
        action_method(payload)

    def default_action(self, payload):
        self.logger('warning', 'Unknown or missing action')
        response = {
            'action': 'ERROR',
            'reason': 'Unknown action',
        }
        self.sendMessage(json.dumps(response).encode('utf-8'))

    def chat_message_action(self, payload):
        self.logger('info', 'Chat message')
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
        self.factory.broadcast(response)

    def player_updated_action(self, payload):
        self.logger('info', 'Updated')

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
        self.factory.send_player_list()

    def send_player_updated(self, previous_info, current_info):
        response = {
            'action': 'PLAYER_UPDATED',
            'uid': self.player.UID,
            'previous': previous_info,
            'current': current_info,
        }
        self.factory.broadcast(response)

    def player_status_action(self, payload):
        self.logger('info', f'Changed status to: {payload["status"]}')
        if payload['status'] == 'ready':
            self.player.set_ready()
            self.send_player_status('ready')
        else:
            self.player.set_not_ready()
            self.send_player_status('not_ready')

    def send_player_status(self, status):
        response = {
            'action': 'PLAYER_STATUS',
            'status': status,
            'name': self.player.name,
            'colour': self.player.colour,
            'gender': self.player.gender,
        }
        self.factory.broadcast(response)

    def throw_dices_action(self, payload):
        self.logger('info', 'Throwed dices')
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
