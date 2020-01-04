"""
Module: factory
"""
from autobahn.asyncio.websocket import WebSocketServerFactory
from moneygather.server.exceptions import GameAlreadyStarted
from moneygather.server.exceptions import GameIsFull
from moneygather.server.game import Game
from moneygather.server.log import logger
from moneygather.server.player import Player

import asyncio
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
        player = Player(client)

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
            self.game.remove_player(client.player)
        except ValueError:
            pass
        else:
            self.send_game_event('PLAYER_DISCONNECTED', client.player.to_json())
            self.send_player_list()

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

    def get_player_list(self):
        """ Constructs the player list from the registered clients.
        """
        player_list = []
        for client in self.clients:
            player = client.player.to_json()
            player_list.append(player)
        return player_list

    # def client_is_ready(self):
    #     self.clients_ready += 1
    #     if self.clients_ready == 4:
    #         self.starting_game()

    # def client_is_not_ready(self):
    #     self.clients_ready -= 1

    # def starting_game(self):
    #     logger.info('SERVER ==> Starting game')
    #     # self.status = STARTING
    #     response = {
    #         'action': 'STARTING_GAME',
    #     }
    #     self.broadcast(json.dumps(response).encode('utf-8'))

    #     asyncio.ensure_future(self.excecute_with_timeout(10, self.start_game))

    # def start_game(self):
    #     logger.info('SERVER ==> Game started')
    #     # self.status = STARTED
    #     response = {
    #         'action': 'STARTED',
    #     }
    #     self.broadcast(json.dumps(response).encode('utf-8'))

    # async def excecute_with_timeout(self, timeout, func):
    #     await asyncio.sleep(timeout)
    #     func()
