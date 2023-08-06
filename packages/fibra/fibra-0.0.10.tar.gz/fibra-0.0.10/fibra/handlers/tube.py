"""
Implements 'pipe' like functionality.
"""



class TubePush(object):
    def __init__(self, tube, arg):
        self.tube = tube
        self.arg = arg


class TubePop(object):
    def __init__(self, tube):
        self.tube = tube


class Tube(object):
    def __init__(self):
        self.queue = []
        self.pushing = []
        self.popping = []

    def push(self, arg):
        return TubePush(self, arg)

    def pop(self):
        return TubePop(self)


class TubeHandler(object):
    handled_types = TubePush, TubePop
    wait = False

    def handle(self, v, task):
        tube = v.tube
        if v.__class__ is TubePush:
            if tube.popping:
                self.schedule.install(tube.popping.pop(0), v,arg)
                self.schedule.install(task)
                self.wait = True
            else:
                tube.pushing.append((task, v.arg))
        if v.__class__ is TubePop:
            if tube.pushing:
                t,v = tube.pushing.pop(0)
                self.schedule.install(t)
                self.schedule.install(task, v)
                self.wait = True
            else:
                tube.popping.append(task)
            
    def is_waiting(self):
        wait = self.wait
        self.wait = False
        return wait

