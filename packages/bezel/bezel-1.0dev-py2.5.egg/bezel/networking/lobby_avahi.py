import avahi
import dbus
from dbus.mainloop import glib
import gobject

gobject.threads_init()
glib.threads_init()

from bezel.networking.lobby import BaseLobby

class AvahiLobby(BaseLobby):
    def __init__(self, *args, **kwargs):
        super(AvahiLobby, self).__init__(*args, **kwargs)

        self.server = None
        self.mainloop = gobject.MainLoop()

        loop = dbus.mainloop.glib.DBusGMainLoop()

        bus = dbus.SystemBus(mainloop=loop)

        self.server = dbus.Interface(
            bus.get_object(avahi.DBUS_NAME, avahi.DBUS_PATH_SERVER),
            avahi.DBUS_INTERFACE_SERVER
        )

        domain = self.server.GetDomainName()

        interface = avahi.IF_UNSPEC
        protocol = avahi.PROTO_INET

        browser = dbus.Interface(
            bus.get_object(avahi.DBUS_NAME,
                           self.server.ServiceBrowserNew(interface, protocol,
                                                         self.stype, domain,
                                                         dbus.UInt32(0))
                          ),
            avahi.DBUS_INTERFACE_SERVICE_BROWSER
        )

        browser.connect_to_signal('ItemNew', self.handler.add_service)
        browser.connect_to_signal('ItemRemove', self.handler.remove_service)

    def resolve_service(self, interface, protocol, name, stype, domain, flags):
        resolved = self.server.ResolveService(interface, protocol, name,
                                              stype, domain,
                                              avahi.PROTO_UNSPEC,
                                              dbus.UInt32(0))
        return resolved[7:9] # host, port

    def run(self):
        self.mainloop.run()

    def stop(self):
        if self.running:
            self.mainloop.quit()

        super(AvahiLobby, self).stop()

