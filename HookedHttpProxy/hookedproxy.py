
from ast import Assert
from importlib.resources import path
from urllib.parse import quote as urlquote, urlparse, urlunparse

from twisted.internet import reactor
from twisted.web import http, proxy, server
from twisted.web.resource import Resource
from twisted.web.server import NOT_DONE_YET
from twisted.web.http import Request, HTTPChannel

from HookedHttpProxy.hook import registered

import traceback
#TODO: take this logging stuff out of here. 
#Only use logging in classes that are independent of our framework
import logging

log = logging.getLogger("__main__")

class HookedHTTPChannel(HTTPChannel):

    def __init__(self):
        super().__init__()

    def requestDone(self, request):

        return super().requestDone(request)


class HookedProxyClient(proxy.ProxyClient):
    
    def __init__(self,command, rest, version, headers, data, father):
        super().__init__(command, rest, version, headers, data, father)


class HookedProxyClientFactory(proxy.ProxyClientFactory):
    protocol = HookedProxyClient
    #protocol = proxy.ProxyClient

    def __init__(self, command, rest, version, headers, data, father):
        super().__init__(command, rest, version, headers, data, father)


class HookedReverseProxyResource(proxy.ReverseProxyResource): 
    #hookedProxyClientFactoryClass = HookedProxyClientFactory
    hookedProxyClientFactoryClass = proxy.ProxyClientFactory


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

        #Request.getAllHeaders()
        #Request.content.s

        
        method  = request.method
        path    = request.path
        headers = request.getAllHeaders()
        body    = request.content.read()
        request.content.seek(0)

        
        try:
            
            for class_name,class_object in registered.items():
                log.debug(f"Applying hook {class_name}")
                method, path, headers, body = class_object.handle_request(
                    class_object, 
                    method,
                    path,
                    headers,
                    body,
                )

        except KeyboardInterrupt:
            #pass exception up the chain
            raise KeyboardInterrupt
        except NotImplementedError:
            traceback.print_exception()
        except AssertionError:
            traceback.print_exception()
        
        except Exception:
            traceback.print_exception()

        
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

        log.info(f"Creating reverse proxy to http://{rhost}:{rport}")
        super().__init__(HookedReverseProxyResource(host, rport, b''))