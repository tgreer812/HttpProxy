from HookedHttpProxy.hook import Hook, enable_hook
import logging

log = logging.getLogger("__main__")

@enable_hook
class ShowMessageHook(Hook):

    hookName = "ShowMessageHook"

    def __init__(self):
        pass


    def handle_request(self, method, path, headers, body):
        print(method.decode(), path.decode())
        for header,value in headers.items():
            print(header.decode() + ":", value.decode())
        print(body.decode())     
        return method, path, headers, body
    
    def handle_response(self, code, status, headers, path, body):
        raise NotImplementedError(str(self))


    def __str__ (self):
        return "ShowMessageHook"
