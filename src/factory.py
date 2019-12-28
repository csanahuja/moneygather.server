from autobahn.asyncio.websocket import WebSocketServerFactory
from monopoly import Monopoly
from player import Player

import json


class Factory(WebSocketServerFactory):

    def __init__(self):
        super().__init__()
        self.clients = []
        self.players = {}
        self.num_players = 0
        self.monopoly = Monopoly()

    def register_client(self, client):
        if client not in self.clients:
            self.clients.append(client)

    def unregister_client(self, client):
        if client in self.clients:
            self.clients.remove(client)
            self.players.pop(client.peer, None)

    def add_player(self, player_info, client):
        # if client.peer not in self.players:
        player = Player(index = self.num_players + 1, **player_info)
        self.players[client.peer] = player
        self.num_players += 1
        self.broadcast('PLAYER_ADDED|' + json.dumps(player.toJSON()))

    def send_message(self, message, sender):
        response = {
            'action': 'MESSAGE',
            'status': 'ok',
            'message': message,
            'from': sender,
        }
        self.broadcast(json.dumps(response).encode('utf-8'))

    def broadcast(self, response):
        for c in self.clients:
            preparedMsg = self.prepareMessage(response)
            c.sendPreparedMessage(preparedMsg)
