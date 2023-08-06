#!/usr/bin/env python
from bezel.networking.lobby import GameLobby
from bezel.networking.client import JSONGameClient

import time
import sys

# Horrible hack to make stdin non-blocking.
import fcntl, os
fcntl.fcntl(0, fcntl.F_SETFL, os.O_NONBLOCK)

class Handler(object):
    def __init__(self):
        self.servers = []
        self.inp = ''
    
    def add_service(self, *args):
        self.servers.append(args)
    
    def remove_service(self, *args):
        self.servers.remove(args)
    
    def get_input(self):
        n = None
        try:
            c = raw_input()
        except EOFError:
            if len(self.inp) > 0:
                try:
                    n = int(self.inp)
                    n = self.servers[n - 1]
                except (ValueError, IndexError):
                    pass
                self.inp = ''
        else:
            self.inp += c
        return n
    
    def __str__(self):
        value = '\033[H\033[2J'
        value += 'Type the number of the server, and press enter:\n'
        value += '-' * 30 + '\n'
        value += '\n'.join(['%d %s' % (i+1, s) for i, s in
                            enumerate(self.servers)]) + '\n'
        value += '-' * 30
        return value

handler = Handler()
lobby = GameLobby('_game._tcp', handler)
lobby.start()

service = None
while service is None:
    print handler
    time.sleep(0.25)
    service = handler.get_input()

host, ip = lobby.resolve_service(*service)

print 'Connecting to %s %s...' % (host, ip),
client = JSONGameClient(host, ip)
print 'done.'

engine = client.engine
print engine.say('blah')

print 'count + 1 =', engine.add(1)

