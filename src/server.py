from autobahn.asyncio.websocket import WebSocketServerFactory
from autobahn.asyncio.websocket import WebSocketServerProtocol
from monopoly import Monopoly
from player import Player

import asyncio
import json


class MonopolyServerProtocol(WebSocketServerProtocol):

    def onConnect(self, request):
        print('Client connecting: {0}'.format(request.peer))

    def onOpen(self):
        print("WebSocket connection open.")
        self.factory.register_client(self)

    def onMessage(self, payload, isBinary):
        payload = payload.decode('utf8')
        payload = payload.split('|')
        action = payload[0]
        print(f'PROCESSING ACTION: {action}')

        if action == 'ADD_PLAYER':
            data = json.loads(payload[1])
            self.factory.add_player(data, self)

        if action == 'MESSAGE':
            msg = "{} from {}".format(payload[1], self.peer)
            self.factory.send_message(msg)

        # payload = payload.decode('utf-8')
        # print('Message received: {0}'.format(payload))
        # if payload == 'UPDATE_CREDIT':
        #     self.monopoly.credit += 100
        # if payload == 'CLEAR_CREDIT':
        #     self.monopoly.credit = 0
        # self.sendMessage(str(self.monopoly.credit).encode('utf-8'), isBinary)

    def onClose(self, wasClean, code, reason):
        print("WebSocket connection closed: {0}".format(reason))
        self.factory.unregister_client(self)


class MonopolyServerFactory(WebSocketServerFactory):

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


if __name__ == '__main__':

    factory = MonopolyServerFactory()
    factory.protocol = MonopolyServerProtocol

    loop = asyncio.get_event_loop()
    coro = loop.create_server(factory, '0.0.0.0', 9000)
    server = loop.run_until_complete(coro)

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.close()
        loop.close()
