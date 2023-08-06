from collections import defaultdict


class Send(object):
    def __init__(self, type, *args):
        self.type = type
        self.args = args


class Recv(object):
    def __init__(self, type):
        self.type = type


class MessagePlugin(object):
    def __init__(self):
        self.handled_types = [Send, Recv]
        self.receiving = defaultdict(list)
        self.sending = defaultdict(list)
        self.pending = list()

    def is_waiting(self):
        install = self.schedule.install
        sending = self.sending
        receiving = self.receiving
        pending = []
        for p in self.pending:
            if p in sending:
                task, args = sending[p].pop(0)
                map(lambda x: install(x, args), receiving[p])
                receiving[p][:] = []
                install(task)
                if not sending[p]: sending.pop(p)
            else:
                pending.append(p)
        self.pending[:] = pending
        return len(self.sending) > 0

    def handle(self, msg, task):
        if msg.__class__ is Recv:
            self.receiving[msg.type].append(task)
            self.pending.append(msg.type)
        elif msg.__class__ is Send:
            self.sending[msg.type].append((task, msg.args))

