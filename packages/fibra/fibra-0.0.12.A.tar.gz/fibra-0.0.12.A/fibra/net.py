import socket
import struct
import time

from fibra.handlers.tasks import Return, Async
from fibra.handlers.io import Read, Write
from fibra.handlers.nonblock import Unblock

from errno import EALREADY, EINPROGRESS, EWOULDBLOCK, ECONNRESET, ENOTCONN, ESHUTDOWN, EINTR, EISCONN


def listen(address, accept_task):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setblocking(0)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(address)
    sock.listen(5)
    while True:
        yield Read(sock.fileno())
        yield Async(accept_task(*sock.accept()))


def connect(address, timeout=0):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    yield Unblock()
    sock.connect(address)
    sock.setblocking(0)
    yield Write(sock.fileno(), timeout)
    yield Return(sock)
    

def recv(sock, length=None, timeout=0):
    yield Read(sock.fileno())    
    if length is None:
        yield Return(sock.recv(4096))
    else:
        while length > 0:
            data = sock.recv(length)
            if data == "":
                raise socket.error
            length -= len(data)
            if length > 0: yield Read(sock.fileno(), timeout)
        yield Return(data)


def line_recv(sock, terminator="\n", timeout=0):
    stream = ""
    abort = False
    while True: 
        yield Read(sock.fileno(), timeout)    
        data = sock.recv(4096)
        if data == "":
            abort = True
        stream += data
        lines = stream.split(terminator)
        if len(lines) > 1:
            for line in lines[:-1]:
                yield Return(line)
        if abort:
            raise socket.error
        stream = lines[-1]


def send(sock, data, timeout=0):
    fd = sock.fileno()
    while data: 
        yield Write(fd, timeout)
        c = sock.send(data)
        data = data[c:]


def send_frame(sock, msg):
    size = struct.pack("!i", len(msg))
    yield send(sock, size + msg)


def recv_frame(sock):
    data = yield recv(sock, 4)
    size, = struct.unpack("!i", data)
    if size > 1024*1024: 
        raise socket.error
    msg = yield recv(sock, size)
    yield Return(msg)

