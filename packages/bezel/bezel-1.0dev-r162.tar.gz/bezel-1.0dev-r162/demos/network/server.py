#!/usr/bin/env python
from bezel.networking.engine import JSONRequestHandler
from bezel.networking.server import ServiceMixin, GameServer, TCPServer

from engine import GameEngine

from random import randint

class MyGameServer(ServiceMixin, GameServer, TCPServer):
    pass

def serve():
    engine = GameEngine()

    port = randint(2000, 8000)
    name = 'My Game Server %d' % port
    stype = '_game._tcp'
    address = ('', port)
    
    server = MyGameServer(name, stype, engine, address, JSONRequestHandler)
    
    try:
        server.serve_forever()
    except:
        server.server_close()

serve()

