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
            print("unregistered client {}".format(client.peer))
            self.clients.remove(client)
            self.players.pop(client.peer, None)

    def add_player(self, player_info, client):
        # if client.peer not in self.players:
        player = Player(index = self.num_players + 1, **player_info)
        self.players[client.peer] = player
        self.num_players += 1
        self.broadcast('PLAYER_ADDED|' + json.dumps(player.toJSON()))

    def send_message(self, msg):
        self.broadcast('MESSAGE|' + msg)

    def broadcast(self, msg):
        print("broadcasting prepared message '{}' ..".format(msg))
        for c in self.clients:
            preparedMsg = self.prepareMessage(msg.encode('utf-8'))
            c.sendPreparedMessage(preparedMsg)
            print("prepared message sent to {}".format(c.peer))