import select
import time



class Request(object):
    id = 0
    def __init__(self, name, *args, **kw):
        self.id += 1
        self.request = 'req', self.id, (name, args, kw)


class Response(object):
    def __init__(self, id, value):
        self.response = 'res', id, value


class RequestResponseHandler(object):
    handled_types = [Request, Response]

    def __init__(self):
        pass

    def pre_schedule(self):
        pass
    
    def handle(self, event, task):
        pass

