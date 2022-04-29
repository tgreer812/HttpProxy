

class Hook():

    def __init__(self):
        pass

    def handle_request(self):
        raise AssertionError("Handle Request Not Implemented")

    def handle_response(self):
        raise AssertionError("Handle Response Not Implemented")