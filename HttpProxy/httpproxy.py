from twisted.internet import reactor
from twisted.web import http, proxy, server

import logging

log = logging.getLogger("driver")

class HookedHTTPChannel(http.HTTPChannel):

    def __init__(self):
        super().__init__()


class HttpHookedClientFactory():

    def dataReceived(self, data):
        self.transport.write(data)



class HookedReverseProxyResource():
    pass


class HookedSite(server.Site):

    def __init__(self, rhost, rport):
        host = f"{rhost}"

        log.info("Creating reverse proxy to http://{rhost}:{rport}")
        super().__init__(proxy.ReverseProxyResource(host, rport, b''))