from autobahn.asyncio.websocket import WebSocketServerFactory
from monopoly import Monopoly


class Factory(WebSocketServerFactory):

    def __init__(self):
        super().__init__()
        self.clients = []
        self.monopoly = Monopoly()

    @property
    def num_players(self):
        return len(self.clients)
    
    def register_client(self, client):
        if client not in self.clients:
            self.clients.append(client)


    def unregister_client(self, client):
        if client in self.clients:
            self.clients.remove(client)

    def broadcast(self, response):
        preparedMsg = self.prepareMessage(response)
        for client in self.clients:
            client.sendPreparedMessage(preparedMsg)
