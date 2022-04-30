
from urllib.parse import quote as urlquote, urlparse, urlunparse

from twisted.internet import reactor
from twisted.web import http, proxy, server
from twisted.web.resource import Resource
from twisted.web.server import NOT_DONE_YET
from twisted.web.http import Request, HTTPChannel

import logging

log = logging.getLogger("__main__")

class HookedHTTPChannel(HTTPChannel):

    def __init__(self):
        super().__init__()


class HookedProxyClient(proxy.ProxyClient):
    
    def __init__(self,command, rest, version, headers, data, father):
        super().__init__(command, rest, version, headers, data, father)

class HookedProxyClientFactory(proxy.ProxyClientFactory):
    protocol = HookedProxyClient

    def __init__(self, command, rest, version, headers, data, father):
        log.debug(f"father type: {type(father)}")
        super().__init__(command, rest, version, headers, data, father)

class HookedReverseProxyResource(proxy.ReverseProxyResource): 
    hookedProxyClientFactoryClass = HookedProxyClientFactory

    #might need to add hooks here?

    def getChild(self, path, request):
        '''
        '''
        return HookedReverseProxyResource(
            self.host,
            self.port,self.path + b"/" + urlquote(path, safe=b"").encode("utf-8")
        )


    def render(self, request):
        if self.port == 80:
            host = self.host
        else:
            host = "%s:%d" % (self.host, self.port)
        
        request.requestHeaders.setRawHeaders(b"host", [host.encode("ascii")])
        request.content.seek(0,0)
        qs = urlparse(request.uri)[4]
        if qs:
            rest = self.path + b"?" + qs
        else:
            rest = self.path
        hookedClientFactory = self.hookedProxyClientFactoryClass(
            request.method,
            rest,
            request.clientproto,
            request.getAllHeaders(),
            request.content.read(),
            request,
        )
        self.reactor.connectTCP(self.host, self.port, hookedClientFactory)
        return NOT_DONE_YET


class HookedReverseProxyRequest(proxy.ReverseProxyRequest):
    proxyClientFactoryClass = HookedProxyClientFactory

class HookedReverseProxy(HookedHTTPChannel):
    requestFactory = HookedReverseProxyRequest





class HookedSite(server.Site):

    def __init__(self, rhost, rport):
        host = f"{rhost}"

        print("hooked site init called")
        log.info("Creating reverse proxy to http://{rhost}:{rport}")
        super().__init__(HookedReverseProxyResource(host, rport, b''))