from autobahn.asyncio.websocket import WebSocketServerFactory
from log import logger
from monopoly import Monopoly

import asyncio
import json


# Player STATUS
NOT_STARTED = 0
STARTING = 1
STARTED = 2


class Factory(WebSocketServerFactory):


    def __init__(self):
        super().__init__()
        self.clients = []
        self.clients_ready = 0
        self.status = NOT_STARTED
        self.monopoly = Monopoly()

    def broadcast(self, response):
        preparedMsg = self.prepareMessage(response)
        for client in self.clients:
            client.sendPreparedMessage(preparedMsg)

    @property
    def num_clients(self):
        return len(self.clients)
    
    def register_client(self, client):
        if self.status != NOT_STARTED:
            client.sendClose(code = 3000, reason='Game already started')
        elif client not in self.clients:
            self.clients.append(client)
            self.monopoly.add_player(client.player)
            self.client_connection(client.player, 'PLAYER_CONNECTED')

    def unregister_client(self, client):
        if client in self.clients:
            self.clients.remove(client)
            self.monopoly.remove_player(client.player)
            self.client_connection(client.player, 'PLAYER_DISCONNECTED')

    def client_connection(self, player, action):
        response = {
            'action': action,
            'name': player.name,
            'colour': player.colour,
            'gender': player.gender,
        }
        self.broadcast(json.dumps(response).encode('utf-8'))

    def client_is_ready(self):
        self.clients_ready += 1;
        if self.clients_ready == 4:
            self.starting_game()

    def client_is_not_ready(self):
        self.clients_ready -= 1;

    def starting_game(self):
        logger.info('SERVER ==> Starting game')
        self.status = STARTING
        response = {
            'action': 'STARTING_GAME',
        }
        self.broadcast(json.dumps(response).encode('utf-8'))

        asyncio.ensure_future(self.excecute_with_timeout(10, self.start_game))

    def start_game(self):
        logger.info('SERVER ==> Game started')
        self.status = STARTED
        response = {
            'action': 'STARTED',
        }
        self.broadcast(json.dumps(response).encode('utf-8'))

    async def excecute_with_timeout(self, timeout, func):
        await asyncio.sleep(timeout)
        func()
