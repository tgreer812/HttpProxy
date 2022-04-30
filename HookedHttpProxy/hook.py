
from HookedHttpProxy.exceptions import OverrideError

registered = {}

def enable_hook(hook_class):
    #TODO: enforce type Hook
    print(type(hook_class))
    registered.update({hook_class.get_name(hook_class): hook_class})


class Hook():
    hookName = "GenericHook"
    
    def __init__(self):
        raise OverrideError("Abstract Hook Must Be Overridden")

    def handle_request(self, code, status, headers, body):
        raise OverrideError("Handle Request Not Implemented")

    def handle_response(self, code, status, headers, body):
        raise OverrideError("Handle Response Not Implemented")

    def get_name(self):
        if(self.hookName == "GenericHook"):
            raise OverrideError("hookName Must Be Overridden")
        return self.hookName