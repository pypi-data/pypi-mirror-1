from collections import defaultdict


class Send(object):
    def __init__(self, type, arg):
        self.type = type
        self.arg = arg


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
                sender, arg = senders.pop(0)
                self.schedule.install(task, arg)
                self.schedule.install(sender, task)
            else:
                self.receiving[msg.type].append(task)
        elif msg.__class__ is Send:
            receivers = self.receiving[msg.type]
            if receivers:
                receiver = receivers.pop(0)
                self.schedule.install(receiver, msg.arg)
                self.schedule.install(task, receiver)
            else:
                self.sending[msg.type].append((task, msg.arg))

