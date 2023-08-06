"""
This module defines low level tasks for working with sockets.

"""
import socket
import struct
import time

from fibra.handlers.tasks import Return, Async
from fibra.handlers.io import Read, Write
from fibra.handlers.nonblock import Unblock

from errno import EALREADY, EINPROGRESS, EWOULDBLOCK, ECONNRESET, ENOTCONN, ESHUTDOWN, EINTR, EISCONN


BUFFER_SIZE = 4096

def listen(address, accept_task):
    """Listen on address, and spawn accept_task when a connection is received."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setblocking(0)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(address)
    sock.listen(5)
    while True:
        yield Read(sock.fileno())
        yield Async(accept_task(*sock.accept()))


def connect(address, timeout=0):
    """Connect to address, and Return a socket on success."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    yield Unblock()
    sock.connect(address)
    sock.setblocking(0)
    yield Write(sock.fileno(), timeout)
    yield Return(sock)
    

def recv(sock, length=None, timeout=0):
    """Receive data from a socket. If length is not None, return length bytes from the socket."""
    yield Read(sock.fileno())    
    if length is None:
        yield Return(sock.recv(BUFFER_SIZE))
    else:
        while length > 0:
            data = sock.recv(length)
            if data == "":
                raise socket.error
            length -= len(data)
            if length > 0: yield Read(sock.fileno(), timeout)
        yield Return(data)


def send(sock, data, timeout=0):
    """Send data through a socket. Task does not finish until all data is sent."""
    fd = sock.fileno()
    while data: 
        yield Write(fd, timeout)
        c = sock.send(data)
        data = data[c:]


def send_line(sock, data, terminator="\n", timeout=0):
    """Send data with a terminator through a socket."""
    yield send(sock, data+terminator, timeout)


def recv_line(sock, terminator="\n", timeout=0):
    """This task continually receives lines from a socket."""
    stream = ""
    abort = False
    while True: 
        yield Read(sock.fileno(), timeout)    
        data = sock.recv(BUFFER_SIZE)
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


def send_frame(sock, msg):
    """Send a frame (a size prefixed string) through a socket."""
    size = struct.pack("!i", len(msg))
    yield send(sock, size + msg)


def recv_frame(sock, timeout=0):
    """Continually Receive frames (a size prefixed string) from a socket."""
    stream = ""
    abort = False
    while True: 
        yield Read(sock.fileno(), timeout)    
        data = sock.recv(BUFFER_SIZE)
        if data == "":
            abort = True
        stream += data
        if len(stream) > 4:
            size, = struct.unpack("!i", stream[:4])
            if size > 1024*1024: 
                raise socket.error
            stream = stream[4:]
            while len(stream) < size:
                yield Read(sock.fileno(), timeout)    
                data = sock.recv(BUFFER_SIZE)
                if data == "":
                    abort = True
                stream += data
                if abort and len(stream) < size: break
            yield Return(stream[:size])
            stream = stream[size:] 

        if abort:
            raise socket.error

