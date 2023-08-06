"""
Implements 'pipe' like functionality.
"""

class TubePush(object):
    def __init__(self, tube):
        self.tube = tube

class TubePop(object):
    def __init__(self, tube):
        self.tube = tube

class Tube(object):
    def __init__(self):
        self.queue = []
        self.waiting = []

    def push(self, arg):
        self.queue.append(arg)
        return TubePush(self)

    def pop(self):
        return TubePop(self)


class TubeHandler(object):
    handled_types = TubePush, TubePop
    waiting_tasks = []
    wait = False

    def handle(self, v, task):
        self.wait = False
        tube = v.tube
        if v.__class__ is TubePush:
            self.wait = True
            self.schedule.install(task)
        if v.__class__ is TubePop:
            if tube.queue:
                self.schedule.install(task, tube.queue.pop(0))
            else:
               self.waiting_tasks.append((task, tube))
            
    def is_waiting(self):
        waiting_tasks = []
        for task, tube in self.waiting_tasks:
            if tube.queue:
                self.schedule.install(task, tube.queue.pop(0))
            else:
                waiting_tasks.append((task, tube))
        self.waiting_tasks[:] = waiting_tasks
        return self.wait

