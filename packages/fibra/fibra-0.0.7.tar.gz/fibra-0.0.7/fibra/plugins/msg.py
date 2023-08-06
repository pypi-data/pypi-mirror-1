from collections import defaultdict


class Send(object):
    def __init__(self, type, *args):
        self.type = type
        self.args = args


class Recv(object):
    def __init__(self, type):
        self.type = type


class MessagePlugin(object):
    handled_types = [Send, Recv]
    receiving = defaultdict(list)
    sending = defaultdict(list)

    def is_waiting(self):
        return False

    def handle(self, msg, task):
        if msg.__class__ is Recv:
            senders = self.sending[msg.type]
            if senders:
                sender, args = senders.pop(0)
                self.schedule.install(task, args)
                self.schedule.install(sender, task)
            else:
                self.receiving[msg.type].append(task)
        elif msg.__class__ is Send:
            receivers = self.receiving[msg.type]
            if receivers:
                receiver = receivers.pop(0)
                self.schedule.install(receiver, msg.args)
            else:
                receiver = None
                self.sending[msg.type].append((task, msg.args))
            self.schedule.install(task, receiver)

