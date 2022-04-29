from twisted.internet import reactor
from twisted.web import http, proxy, server


class HookedHTTPChannel(http.HTTPChannel):

    def __init__(self):
        super().__init__()


class HttpHookedRequest(http.request):
    #pass

    def process(self):
        pass


class HttpHookedClientFactory():

    def dataReceived(self, data):
        self.transport.write(data)



class HookedSite(server.site):

    def __init__(self, rhost, rport):
        host = f"{rhost}"
        super().__init__(host, rport, b'')