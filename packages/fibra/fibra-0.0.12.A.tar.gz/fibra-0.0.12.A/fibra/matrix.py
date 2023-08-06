import json
import socket

import fibra
import fibra.net


class BrokenTube(Exception): pass


def dispatch(tube, request):
    action = request['action']
    wait = request['wait']
    if action == 'pop':
        value = yield tube.pop(wait)
        yield fibra.Return(value)
    elif action == 'push':
        yield tube.push(request['value'], wait)


def service_client(sock, address):
    try:
        name = yield fibra.net.recv_frame(sock)
    except socket.error:
        pass
    else:
        tube = fibra.Tube(name)
        while True:
            try:
                msg = yield fibra.net.recv_frame(sock)
            except socket.error:
                break
            try:
                request = json.loads(msg)
            except ValueError, e:
                type = "exception"
                response = str(e)
            else:
                try:
                    response = yield dispatch(tube, request)
                except fibra.EmptyTube:
                    type = "empty"
                    response = None
                except Exception, e:
                    response = str(e)
                    type = "exception"
                else:
                    type = "ok"
            try:
                yield fibra.net.send_frame(sock, json.dumps((type, response)))
            except socket.error:
                break
    sock.close()


def serve(address):
    yield fibra.net.listen(address, service_client)

    
def service_server(sock, namespace):
    while True:
        yield fibra.net.send_frame(sock, json.dumps(dict(action="list")))
        response = yield fibra.net.recv_frame(sock)
        
        type, response = json.loads(response)
        if type == "exception":
            raise Exception(response)
        if type == "ok":
            for name in response:
                local_name = "%s.%s" % (namespace, name)
                if local_name not in fibra.Tube.instances:
                    fibra.Tube.instances[local_name] = RemoteTube(sock, name)
        yield 1.0


def connect(address, names, namespace='remote', reconnect=True):
    for name in names:
        task = link(address, namespace, name, reconnect)
        yield fibra.Async(task)


def link(address, namespace, name, reconnect=True):
    sock = yield fibra.net.connect(address)
    yield fibra.net.send_frame(sock, name)
    local_name = "%s.%s" % (namespace, name)
    if local_name not in fibra.Tube.instances:
        fibra.Tube.instances[local_name] = RemoteTube(address, namespace, name, reconnect)
    fibra.Tube.instances[local_name].sock = sock
    

def wait_for_tube(name):
    while name not in fibra.Tube.instances:
        yield 0.1
    yield fibra.Return(fibra.Tube(name))


class RemoteTube(object):
    def __init__(self, address, namespace, name, reconnect):
        self.sock = None
        self.address = address
        self.namespace = namespace
        self.name = name
        self.reconnect = reconnect

    def connect(self):
        if self.reconnect:
            print "Lost link", self, "reconnecting..."
            yield link(self.address, self.namespace, self.name)
        else:
            raise BrokenPipe()

    def push(self, value, wait=False):
        while True:
            try:
                yield fibra.net.send_frame(self.sock, json.dumps(dict(action="push", value=value, wait=wait)))
                response = yield fibra.net.recv_frame(self.sock)
            except socket.error:
                yield self.connect()
            else:
                break
        type, response = json.loads(response)
        if type == "empty":
            raise fibra.EmptyTube()
        if type == "exception":
            raise Exception(response)
        yield fibra.Return(response)
        
    def pop(self, wait=True):
        while True:
            try:
                yield fibra.net.send_frame(self.sock, json.dumps(dict(action="pop", wait=wait)))
                response = yield fibra.net.recv_frame(self.sock)
            except socket.error:
                yield self.connect()
            else:
                break
        type, response = json.loads(response)
        if type == "empty":
            raise fibra.EmptyTube()
        if type == "exception":
            raise Exception(response)
        yield fibra.Return(response)
        

