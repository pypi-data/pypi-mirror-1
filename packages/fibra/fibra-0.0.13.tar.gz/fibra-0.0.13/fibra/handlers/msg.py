from collections import defaultdict



class SendMsg(object):
    def __init__(self, type, *args):
        self.type = type
        self.args = args


class RecvMsg(object):
    def __init__(self, type):
        self.type = type


class MessageHandler(object):
    def __init__(self):
        self.handled_types = [SendMsg, RecvMsg]
        self.receiving = defaultdict(list)
        self.sending = defaultdict(list)
        self.pending = list()

    def pre_schedule(self):
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
        if msg.__class__ is RecvMsg:
            self.receiving[msg.type].append(task)
            self.pending.append(msg.type)
        elif msg.__class__ is SendMsg:
            self.sending[msg.type].append((task, msg.args))

