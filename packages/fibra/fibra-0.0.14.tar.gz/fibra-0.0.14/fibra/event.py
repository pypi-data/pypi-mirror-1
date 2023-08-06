"""
The fibra.event module provides pubsub style functions
for tasks over TCP.
"""

import fibra
import fibra.net

schedule = fibra.schedule()

class Connection(object):
    """
    A base connection class for fibra.event.
    """
    def __init__(self, transport):
        self.protocol = Protocol(transport)
        self.outbox = fibra.Tube()
        self._closed = False

    def start(self):
        yield fibra.Async(self.receiver())
        yield fibra.Async(self.sender())

    def send(self, top, headers, body):
        pass

    def sender(self):
        while True:
            top, headers, body = yield self.outbox.pop()
            try:
                yield self.protocol.send(top, headers, body)
            except Exception, e:
                print "Connection lost:", e
                break
        self.close()

    def receiver(self):
        while True:
            try:
                top, headers, body = yield self.protocol.recv()
            except Exception, e:
                print "Connection lost:", e
                break
            self.dispatch(top, headers, body)
        self.close()

    def dispatch(self, top, headers, body):
        pass

    def close(self):
        if not self._closed:
            self._closed = True
            self.protocol.close()

    def __del__(self):
        self.close()


class Protocol(object):
    """
    A line based protocol for fibra.event.
    """
    def __init__(self, transport):
        self.transport = transport

    def recv(self):
        top = yield self.transport.recv_line()
        headers = yield self.collect_headers()
        try:
            size = int(headers.get('content-length', ""))
        except ValueError:
            body = "" 
        else:
            body = yield self.transport.recv(size)
        yield fibra.Return((top, headers, body))

    def send(self, top, headers, body=""):
        if body:
            headers['content-length'] = "%s"%len(body)
        data = top + "\n" + "\n".join(":".join(i) for i in headers.items()) + "\n\n" + body
        yield self.transport.send(data)
            
    def collect_headers(self):
        headers = {}
        while True:
            line = yield self.transport.recv_line()
            if line == "": break
            i = line.index(":")
            k, v = line[:i].lower(), line[i+1:]
            headers[k] = v
        yield fibra.Return(headers)

    def close(self):
        self.transport.close()


class ClientConnection(Connection):
    """
    A connection from a fibra.event client.
    """
    listeners = {}
    def __init__(self, *args, **kw):
        Connection.__init__(self, *args, **kw)
        self.subscriptions = set()

    def publish(self, headers, body):
        for s in self.listeners.setdefault(headers['name'], set()):
            yield s.outbox.push(("message", headers, body))

    def dispatch(self, top, headers, body):
        if top == "subscribe":
            self.listeners.setdefault(headers['name'], set()).add(self)
            self.subscriptions.add(headers['name'])
        elif top == "publish":
            schedule.install(self.publish(headers, body))
        else:
            method = getattr(self, 'do_%s'%top, None)
            if method is not None:
                method(headers, body)
            else:
                self.close()

    def close(self):
        for i in self.subscriptions:
            self.listeners[i].discard(self)
        Connection.close(self)
    

class ServerConnection(Connection):
    """
    A connection to a fibra.event server.
    """
    def __init__(self, *args, **kw):
        Connection.__init__(self, *args, **kw)
        schedule.install(self.start())

    def dispatch(self, top, headers, body):
        if top == "message":
            self.recv_message(headers, body)
        else:
            method = getattr(self, 'do_%s'%top, None)
            if method is not None:
                method(headers, body)
            else:
                self.close()

    def recv_message(self, headers, body):
        pass

    def push(self, name, headers, body):
        def task():
            yield self.outbox.push((name, headers, body))
        schedule.install(task())

    def publish(self, name, headers, body):
        headers["name"] = name
        headers["content-length"] = "%s"%len(body)
        self.push("publish", headers, body)

    def subscribe(self, name):
        self.push("subscribe", dict(name=name), "")
        
        
