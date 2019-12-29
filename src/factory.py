from autobahn.asyncio.websocket import WebSocketServerFactory
from monopoly import Monopoly

import json


class Factory(WebSocketServerFactory):

    def __init__(self):
        super().__init__()
        self.clients = []
        self.monopoly = Monopoly()

    @property
    def num_clients(self):
        return len(self.clients)
    
    def register_client(self, client):
        if client not in self.clients:
            self.clients.append(client)
            self.monopoly.add_player(client.player)
            self.client_connection(client.player, 'PLAYER_CONNECTED')

            if self.num_clients == 4:
                self.start_game()

    def unregister_client(self, client):
        if client in self.clients:
            self.clients.remove(client)
            self.monopoly.remove_player(client.player)
            self.client_connection(client.player, 'PLAYER_DISCONNECTED')

    def broadcast(self, response):
        preparedMsg = self.prepareMessage(response)
        for client in self.clients:
            client.sendPreparedMessage(preparedMsg)

    def client_connection(self, player, action):
        response = {
            'action': action,
            'name': player.name,
            'colour': player.colour,
            'gender': player.gender,
        }
        self.broadcast(json.dumps(response).encode('utf-8'))

    def start_game(self):
        response = {
            'action': 'STARTING_GAME',
        }

        self.broadcast(json.dumps(response).encode('utf-8'))
