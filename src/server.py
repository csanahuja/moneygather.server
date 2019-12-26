from autobahn.asyncio.websocket import WebSocketServerFactory
from autobahn.asyncio.websocket import WebSocketServerProtocol
from monopoly import Monopoly

import asyncio
import ssl


class MonopolyServerProtocol(WebSocketServerProtocol):

    def onConnect(self, request):
        print('Client connecting: {0}'.format(request.peer))
        print('Initializing monopoly')
        self.monopoly = Monopoly()

    def onOpen(self):
        print("WebSocket connection open.")

    def onMessage(self, payload, isBinary):
        payload = payload.decode('utf-8')
        print('Message received: {0}'.format(payload))
        if payload == 'UPDATE_CREDIT':
            self.monopoly.credit += 100
        if payload == 'CLEAR_CREDIT':
            self.monopoly.credit = 0
        print('Current credit: {0}'.format(self.monopoly.credit))
        self.sendMessage(str(self.monopoly.credit).encode('utf-8'), isBinary)

    def onClose(self, wasClean, code, reason):
        print("WebSocket connection closed: {0}".format(reason))


if __name__ == '__main__':

    factory = WebSocketServerFactory()
    factory.protocol = MonopolyServerProtocol

    sslcontext = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
    sslcontext.load_cert_chain(
        '/etc/httpd/certificates/niticras.crt',
        '/etc/httpd/certificates/niticras.key',
    )

    loop = asyncio.get_event_loop()
    coro = loop.create_server(factory, '0.0.0.0', 9000, ssl=sslcontext)
    server = loop.run_until_complete(coro)

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.close()
        loop.close()
