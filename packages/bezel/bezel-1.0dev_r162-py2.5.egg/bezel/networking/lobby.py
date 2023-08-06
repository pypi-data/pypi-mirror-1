import logging
import threading

USE_AVAHI = False
USE_BONJOUR = False

class BaseLobby(object):
    def __init__(self, stype, handler):
        self.stype = stype
        self.handler = handler

        self.thread = None
        self.running = False

    def resolve_service(self, *args, **kwargs):
        """def resolve(self, *args, **kwargs): return host, port"""
        raise NotImplementedError

    def run(self):
        raise NotImplementedError

    def start(self):
        if not self.running:
            self.thread = threading.Thread(target=self.run)
            self.thread.setDaemon(True)
            self.thread.start()

            self.running = True

    def stop(self):
        if self.running:
            self.running = False
            self.thread.join()

try:
    from lobby_avahi import AvahiLobby
except ImportError:
    logging.warn('Avahi could not be imported.')
else:
    logging.debug('Using avahi.')
    USE_AVAHI = True

try:
    from lobby_bonjour import BonjourLobby
except ImportError:
    logging.warn('Pybonjour could not be imported.')
else:
    logging.debug('Using pybonjour.')
    USE_BONJOUR = True

if USE_AVAHI:
    GameLobby = AvahiLobby
elif USE_BONJOUR:
    GameLobby = BonjourLobby

