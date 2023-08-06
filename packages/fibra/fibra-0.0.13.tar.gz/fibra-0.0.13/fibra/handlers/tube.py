"""
Implements 'pipe' like functionality.
"""


class EmptyTube(Exception): pass


class TubePush(object):
    __slots__ = ['tube', 'arg', 'wait']
    def __init__(self, tube, arg, wait):
        self.tube = tube
        self.arg = arg
        self.wait = wait


class TubePop(object):
    __slots__ = ['tube', 'wait']
    def __init__(self, tube, wait):
        self.tube = tube
        self.wait = wait


class Tube(object):
    instances = {}

    def __new__(class_, name=None):
        if name is not None and name in class_.instances:
            return class_.instances[name]
            
        self = object.__new__(class_)
        self.pushing = []
        self.popping = []
        if name is not None:
            class_.instances[name] = self
        return self
 
    def push(self, arg, wait=False):
        return TubePush(self, arg, wait)

    def pop(self, wait=True):
        return TubePop(self, wait)


class TubeHandler(object):
    handled_types = TubePush, TubePop
    wait = False

    def handle(self, v, task):
        tube = v.tube
        if v.__class__ is TubePush:
            if tube.popping:
                self.schedule.install(tube.popping.pop(0), v.arg)
                self.schedule.install(task)
                self.wait = True
            else:
                if v.wait:
                    tube.pushing.append((task, v.arg))
                else:
                    tube.pushing.append((None, v.arg))
                    self.schedule.install(task)
                    self.wait = True
                    
        elif v.__class__ is TubePop:
            if tube.pushing:
                t,v = tube.pushing.pop(0)
                if t: self.schedule.install(t)
                self.schedule.install(task, v)
                self.wait = True
            else:
                if v.wait:
                    tube.popping.append(task)
                else:
                    self.schedule.install(task, EmptyTube())
            
    def pre_schedule(self):
        wait = self.wait
        self.wait = False
        return wait

