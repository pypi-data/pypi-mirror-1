import logging

USE_AVAHI = False
USE_BONJOUR = False

try:
    import avahi
    import dbus
except ImportError:
    logging.warn('Avahi could not be imported.')
else:
    USE_AVAHI = True

try:
    import pybonjour
except ImportError:
    logging.warn('PyBonjour could not be imported.')
else:
    USE_BONJOUR = True

import SocketServer

class TCPServer(SocketServer.TCPServer, object):
    __doc__ = SocketServer.TCPServer.__doc__
class UDPServer(SocketServer.UDPServer, object):
    __doc__ = SocketServer.UDPServer.__doc__

class GameServer(SocketServer.ThreadingMixIn, object):
    def __init__(self, engine, *args, **kwargs):
        self.engine = engine

        super(GameServer, self).__init__(*args, **kwargs)

class BaseZeroconfMixin(object):
    def __init__(self, name, stype, *args, **kwargs):
        self.name = name
        self.stype = stype
        self.domain = kwargs.pop('domain', '')
        self.text = kwargs.pop('text', '')

        super(BaseZeroconfMixin, self).__init__(*args, **kwargs)

if USE_AVAHI:
    class AvahiMixin(BaseZeroconfMixin):
        """
        A mixin which adds Avahi publishing to a TCP server.
        """
        def server_bind(self):
            # Set host to '' because avahi won't register other hostnames.
            host = ''
            port = self.server_address[1]

            # Create the socket.
            super(AvahiMixin, self).server_bind()

            # Register the server through avahi.
            bus = dbus.SystemBus()
            server = dbus.Interface(
                             bus.get_object(
                                     avahi.DBUS_NAME,
                                     avahi.DBUS_PATH_SERVER),
                            avahi.DBUS_INTERFACE_SERVER)

            group = dbus.Interface(
                bus.get_object(avahi.DBUS_NAME, server.EntryGroupNew()),
                avahi.DBUS_INTERFACE_ENTRY_GROUP
            )

            group.AddService(
                avahi.IF_UNSPEC, avahi.PROTO_UNSPEC, dbus.UInt32(0),
                self.name, self.stype, self.domain,
                host, dbus.UInt16(port),
                self.text,
            )

            group.Commit()
            self.group = group

        def server_close(self):
            # Close the server.
            super(AvahiMixin, self).server_close()

            # Unregister the server with avahi.
            self.group.Reset()

if USE_BONJOUR:
    class BonjourMixin(BaseZeroconfMixin):
        def server_bind(self):
            # Create the socket.
            super(BonjourMixin, self).server_bind()

            # Register the server through pybonjour.
            self.service = pybonjour.DNSServiceRegister(
                name=self.name,
                regtype=self.stype,
                port=self.server_address[1],
            )

        def server_close(self):
            # Close the server.
            super(BonjourMixin, self).server_close()

            # Unregister the server with pybonjour.
            self.service.close()
            self.service = None

if USE_AVAHI:
    ServiceMixin = AvahiMixin
elif USE_BONJOUR:
    ServiceMixin = BonjourMixin

