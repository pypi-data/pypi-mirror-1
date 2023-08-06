import select
import time



class Read(object):
    def __init__(self, fd, timeout=0):
        self.fd = fd
        self.timeout = timeout


class Write(object):
    def __init__(self, fd, timeout=0):
        self.fd = fd
        self.timeout = timeout


class IOHandler(object):
    handled_types = [Read, Write]

    def __init__(self):
        self.readers = {}
        self.writers = {}

    def pre_schedule(self):
        readers = self.readers.keys()
        writers = self.writers.keys()
        all = readers + writers

        if all:
            install = self.schedule.install
            r, w, e = select.select(readers, writers, all, 0)
            error = set()
            for i in e:
                raise IOError("Something bad happened.")
            for i in r:
                install(self.readers.pop(i)[0])
            for i in w:
                install(self.writers.pop(i)[0])

        now = time.time()
        for fd, (task, check, timeout) in self.readers.items():
            if check == 0: continue
            if now > timeout:
                self.readers.pop(fd)
                install(task, IOError("read has timed out"))
        for fd, (task, check, timeout) in self.writers.items():
            if check == 0: continue
            if now > timeout:
                self.writers.pop(fd)
                install(task, IOError("write has timed out"))

        return len(self.readers) + len(self.writers)
    
    def handle(self, event, task):
        if event.__class__ is Write:
            if event.fd in self.writers: raise IOError("fd is being used")
            self.writers[event.fd] = task, event.timeout, time.time() + event.timeout
        if event.__class__ is Read:
            if event.fd in self.readers: raise IOError("fd is being used")
            self.readers[event.fd] = task, event.timeout, time.time() + event.timeout
    
