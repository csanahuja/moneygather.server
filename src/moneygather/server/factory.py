"""
Module: factory
"""
from autobahn.asyncio.websocket import WebSocketServerFactory
from moneygather.server.exceptions import GameAlreadyStarted
from moneygather.server.exceptions import GameIsFull
from moneygather.server.game import Game
from moneygather.server.player import Player
from moneygather.server.utils import number_to_string

import json


class Factory(WebSocketServerFactory):

    def __init__(self):
        super().__init__()
        self.clients = []
        self.game = Game(self)

    def register_client(self, client):
        """ Method invoked by protocol (client) instance on open
        Generates a new player and adds it to the game.

        If no exceptions adds the client to the list of client.
        If there are exceptions closes the websocket connection.
        """
        player = Player(client, self.game)

        try:
            self.game.add_player(player)
        except GameAlreadyStarted:
            client.sendClose(code=3000, reason='Game already started')
            return
        except GameIsFull:
            client.sendClose(code=3001, reason='Max players reached')
            return

        client.player = player
        client.send_client_info()
        self.clients.append(client)
        self.send_game_event('PLAYER_CONNECTED', client.player.to_json())
        self.send_player_list()

    def unregister_client(self, client):
        """ Method invoked by protocol (client) instance on closed
        Removes player from the game and client from the list of clients.
        """
        try:
            self.clients.remove(client)
        except ValueError:
            pass
        else:
            self.send_game_event(
                'PLAYER_DISCONNECTED',
                client.player.to_json(),
            )
            self.send_player_list()
            self.game.remove_player(client.player)

    def broadcast(self, response):
        """ Encodes and sends the message to all clients
        """
        response = json.dumps(response).encode('utf-8')
        preparedMsg = self.prepareMessage(response)
        for client in self.clients:
            client.sendPreparedMessage(preparedMsg)

    def send_game_event(self, game_event, data):
        """ Sends a game event message.
        """
        response = {
            'action': 'GAME_EVENT',
            'game_event': game_event,
            'data': data,
        }
        self.broadcast(response)

    def send_player_list(self):
        """ Sends the player list.
        """
        player_list = self.get_player_list()
        response = {
            'action': 'PLAYER_LIST',
            'player_list': player_list,
            'num_players': self.game.num_players
        }
        self.broadcast(response)

    def send_dices_result(self, dices_result):
        """ Sends dices result.
        """
        response = {
            'action': 'DICES_RESULT',
            'dice1': number_to_string(dices_result[0]),
            'dice2': number_to_string(dices_result[1]),
        }
        self.broadcast(response)

    def send_player_movement(self, player):
        """ Sends a player movement.
        """
        response = {
            'action': 'PLAYER_MOVEMENT',
            'position': player.position,
            'uid': player.UID,
        }
        self.broadcast(response)

    def send_player_bankrupt(self, player):
        """ Sends a player bankrupt.
        """
        response = {
            'action': 'PLAYER_BANKRUPT',
            'uid': player.UID,
        }
        self.broadcast(response)

    def send_player_winner(self, player):
        """ Sends the winner player.
        """
        response = {
            'action': 'PLAYER_WINNER',
            'uid': player.UID,
        }
        self.broadcast(response)

    def get_player_list(self):
        """ Constructs the player list from the registered clients.
        """
        player_list = []
        for client in self.clients:
            player = client.player.to_json()
            player_list.append(player)
        return player_list

    def start_game(self):
        """ Starts the game.
        """
        player_list = self.get_player_list()
        board = self.game.board.to_json()
        response = {
            'action': 'GAME_STARTED',
            'player_list': player_list,
            'board': board,
        }
        self.broadcast(response)

    def next_turn(self):
        """ Assigns next turn.
        """
        self.game.next_turn()
