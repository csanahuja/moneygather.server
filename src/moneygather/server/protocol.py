"""
Module: protocol
"""
from autobahn.asyncio.websocket import WebSocketServerProtocol
from moneygather.server.log import logger
from moneygather.server.log import log_exceptions
from moneygather.server.utils import remove_html_tags

import json


class Protocol(WebSocketServerProtocol):

    @log_exceptions
    def onConnect(self, request):
        """ Connected client hook.
        """
        self.logger('info', 'Connecting')

    @log_exceptions
    def onOpen(self):
        """ Opened client hook. Registers the client.
        """
        self.logger('info', 'Opened')
        self.factory.register_client(self)

    @log_exceptions
    def onClose(self, wasClean, code, reason):
        """ Closed client hook. Unregisters the client.
        """
        self.logger('info', f'Closed: Code {code} Reason: {reason}')
        self.factory.unregister_client(self)

    @log_exceptions
    def onMessage(self, payload, isBinary):
        """ Message from client hook. Process the message.
        """
        try:
            self.logger('info', 'Socket message')
            payload = json.loads(payload.decode('utf8'))
        except ValueError:
            response = {
                'action': 'ERROR',
                'reason': 'The message must be JSON',
            }
            self.logger('warning', 'Socket message error')
            self.send_message(response)
        else:
            self.process_message(payload)

    def logger(self, method, message):
        """ Helper function to log including client peer info.
        """
        pre_message = f'CLIENT: {self.peer} ==>'

        if method == 'info':
            logger.info(f'{pre_message} {message}')
        if method == 'warning':
            logger.warning(f'{pre_message} {message}')

    def process_message(self, payload):
        """ Reads the message action and calls the proper handler.
        """
        switcher = {
            'MESSAGE': self.chat_message_action,
            'PLAYER_STATUS': self.player_status_action,
            'PLAYER_UPDATED': self.player_updated_action,
            'ROLL_DICES': self.roll_dices_action,
        }
        action = payload.get('action', False)
        action_method = switcher.get(action, self.default_action)
        action_method(payload)

    def default_action(self, payload):
        """ Default action handler when the message received by the client
        contains an unknown action or no action at all.
        """
        self.logger('warning', 'Unknown or missing action')
        response = {
            'action': 'ERROR',
            'reason': 'Unknown action',
        }
        self.send_message(response)

    def not_allowed_action(self, action):
        """ Action handler when the client tries to perform an action it
        is not allowed in the current workflow state.
        """
        self.logger('warning', f'Not allowed action: {action}')
        response = {
            'action': 'NOT ALLOWED',
            'reason': 'Action not allowed',
        }
        self.send_message(response)

    def chat_message_action(self, payload):
        """ Action handler when received a chat message.
        """
        self.logger('info', 'Chat message')
        message = payload['message']
        message = message.strip()
        if not message:
            return
        message = remove_html_tags(message)
        self.send_chat_message(message)

    def player_status_action(self, payload):
        """ Action handler when player changes its status.
        """
        self.logger('info', f'Changed status to: {payload["status"]}')
        if payload['status'] == 'ready':
            self.factory.send_game_event(
                'PLAYER_READY',
                self.player.to_json(),
            )
            self.player.set_ready()
        else:
            self.factory.send_game_event(
                'PLAYER_NOT_READY',
                self.player.to_json(),
            )
            self.player.set_not_ready()
        self.factory.send_player_list()

    def player_updated_action(self, payload):
        """ Action handler when player updates their attributes.
        """
        self.logger('info', 'Updated')

        name = payload['name']
        colour = payload['colour']
        gender = payload['gender']
        previous_name = self.player.name
        previous_colour = self.player.colour
        previous_gender = self.player.gender

        if (not self.player.update_player_attribute('name', name)
                and not self.player.update_player_attribute('colour', colour)
                and not self.player.update_player_attribute('gender', gender)):
            return

        player_updated_info = {
            'name': self.player.name,
            'colour': self.player.colour,
            'gender': self.player.gender,
            'previous_name': previous_name,
            'previous_colour': previous_colour,
            'previous_gender': previous_gender,
        }

        self.factory.send_game_event('PLAYER_UPDATED', player_updated_info)
        self.factory.send_player_list()

    def roll_dices_action(self, payload):
        """ Action handler when the player rolls the dices.
        """
        self.logger('info', 'Rolled dices')
        self.player.roll_dices()
        # self.factory.next_turn()

    def send_message(self, message):
        """ Encodes the messages and sends to the client.
        """
        message = json.dumps(message).encode('utf-8')
        self.sendMessage(message)

    def send_client_info(self):
        """ Sends to client initial information about the player.
        """
        response = {
            'action': 'PLAYER_INFO',
            'uid': self.player.UID,
            'name': self.player.name,
            'colour': self.player.colour,
            'gender': self.player.gender,
        }
        self.send_message(response)

    def send_chat_message(self, message):
        """ Sends to clients a chat message.
        """
        response = {
            'action': 'MESSAGE',
            'message': message,
            'name': self.player.name,
            'colour': self.player.colour,
            'gender': self.player.gender,
        }
        self.factory.broadcast(response)

    def send_player_turn(self, turn_duration):
        """ Sends the player when it is his turn.
        """
        response = {
            'action': 'PLAYER_TURN',
            'duration': turn_duration,
        }
        self.send_message(response)

    def send_player_end_dices(self):
        """ Sends the player when he cannot roll dices.
        """
        response = {
            'action': 'PLAYER_END_DICES',
        }
        self.send_message(response)
