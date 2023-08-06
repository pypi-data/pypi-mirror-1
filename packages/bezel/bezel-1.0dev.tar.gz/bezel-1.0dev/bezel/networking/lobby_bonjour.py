import logging

import pybonjour
import socket
import select

import os
if os.environ.get('AVAHI_COMPAT_NOWARN'):
    logging.warn('Bonjour on Linux is unstable!')

from bezel.networking.lobby import BaseLobby

class BonjourLobby(BaseLobby):
    def browse_service(self, browser, flags, interface, error_code,
                        service_name, stype, domain):
        if error_code != pybonjour.kDNSServiceErr_NoError:
            raise Exception("PyBonjour Error: %d" % error_code)

        service = (service_name, stype, domain, interface)
        if flags & pybonjour.kDNSServiceFlagsAdd:
            self.handler.add_service(*service)
        else:
            self.handler.remove_service(*service)

    def query_service(self, interface, fullname, rrtype, timeout=5):
        queried = [None]
        def callback(sdRef, flags, interface, error_code, fullname, rrtype,
                     rrclass, rdata, ttl):
            if error_code == pybonjour.kDNSServiceErr_NoError:
                ip = socket.inet_ntoa(rdata)
                queried[0] = ip
            else:
                queried[0] = False

        sdRef = pybonjour.DNSServiceQueryRecord(interfaceIndex=interface,
                                                fullname=fullname,
                                                rrtype=rrtype,
                                                callBack=callback)
        while queried[0] is None:
            ready = select.select([sdRef], [], [], timeout)
            if not sdRef in ready[0]:
                return False
            pybonjour.DNSServiceProcessResult(sdRef)
        sdRef.close()

        return queried[0]

    def resolve_service(self, service_name, stype, domain, interface,
                        timeout=5):
        resolved = [None]
        def callback(sdRef, flags, interface, error_code, fullname,
                    host, port, txt_record):
            if error_code == pybonjour.kDNSServiceErr_NoError:
                resolved[0] = (fullname, host, port, txt_record)
            else:
                resolved[0] = False

        sdRef = pybonjour.DNSServiceResolve(0, interface, service_name,
                                               stype, domain, callback)

        while resolved[0] is None:
            ready = select.select([sdRef], [], [], timeout)
            if not sdRef in ready[0]:
                return False
            pybonjour.DNSServiceProcessResult(sdRef)
        sdRef.close()

        fullname, host, port, txt_record = resolved[0]
        result = self.query_service(interface, fullname,
                                    pybonjour.kDNSServiceType_A)

        return result

    def run(self):
        self.browser = pybonjour.DNSServiceBrowse(regtype=self.stype,
                                                  callBack=self.browse_service)
        while self.running:
            ready = select.select([self.browser], [], [])
            if self.browser in ready[0]:
                pybonjour.DNSServiceProcessResult(self.browser)
        self.browser.close()

