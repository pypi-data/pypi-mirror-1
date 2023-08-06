"""
This module defines low level tasks for working with sockets.

"""
import socket
import struct
import time

from fibra.handlers.tasks import Return, Async
from fibra.handlers.io import Read, Write
from fibra.handlers.nonblock import Unblock


BUFFER_SIZE = 1024 * 1024 
MAX_FRAME_SIZE = 1024*1024


def listen(address, accept_task):
    """Listen on address, and spawn accept_task when a connection is received."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setblocking(0)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(address)
    sock.listen(5)
    while True:
        yield Read(sock.fileno())
        yield Async(accept_task(Transport(sock.accept()[0])))


def connect(address, timeout=0):
    """Connect to address, and Return a transport on success."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    yield Unblock()
    sock.connect(address)
    sock.setblocking(0)
    yield Write(sock.fileno(), timeout)
    yield Return(Transport(sock))

    
class Transport(object):
    """Provides methods for sending and receiving bytes, lines and frames
    over a socket.
    """
    def __init__(self, sock):
        self.sock = sock
        self.stream = ""
        self.aborted = False

    def _fetch(self, timeout=0):
        if self.aborted: raise socket.error
        yield Read(self.sock.fileno(), timeout)    
        data = self.sock.recv(BUFFER_SIZE)
        if data == "":
            self.close()
        else:
            self.stream += data 

    def close(self):
        self.sock.close()
        self.aborted = True

    def recv(self, size, timeout=0):
        """Receive a number of bytes."""
        while len(self.stream) < size:
            yield self._fetch()
        msg = self.stream[:size]
        self.stream = self.stream[size:]
        yield Return(msg)
                
    def recv_frame(self, timeout=0):
        """Receive a frame (a size prefixed string)."""
        while len(self.stream) < 4:
            yield self._fetch()
        size, = struct.unpack("!i", self.stream[:4])
        self.stream = self.stream[4:]
        if size > MAX_FRAME_SIZE: raise socket.error
        while len(self.stream) < size:
            yield self._fetch()
        msg = self.stream[:size]
        self.stream = self.stream[size:] 
        yield Return(msg)

    def recv_line(self, terminator="\n", strip=True, timeout=0):
        """Receive a line terminated by terminator (default \n)"""
        while terminator not in self.stream:
            yield self._fetch()
        index = self.stream.index(terminator)
        line = self.stream[:index]
        self.stream = self.stream[index+len(terminator):]
        if strip: line = line.strip()
        yield Return(line)

    def send(self, data, timeout=0):
        """Send data through a socket. Task does not finish until all data is sent."""
        fd = self.sock.fileno()
        while data: 
            yield Write(fd, timeout)
            c = self.sock.send(data)
            data = data[c:]

    def send_frame(self, msg, timeout=0):
        """Send a frame (a size prefixed string) through a socket."""
        size = struct.pack("!i", len(msg))
        yield self.send(size+msg, timeout)

    def send_line(self, data, terminator="\n", timeout=0):
        """Send data with a terminator through a socket."""
        yield self.send(data+terminator, timeout)

