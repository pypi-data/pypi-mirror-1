import handlers.sleep as sleep
import handlers.tasks as tasks
import handlers.nonblock as nonblock
import handlers.msg as msg
import handlers.tube as tube



class StopIteratorHandler(object):
    """This is the default handler for handling StopIteration exceptions.
    It simply ignores the exception, and does not add the task back into 
    the scheduler.
    """
    handled_types = [StopIteration]
    def is_waiting(self): return False
    def handle(self, exception, task): pass


def hertz(Hz, fn, strict=True):
    """Wrap a generator and run it a Hz frequency.
    """
    T = 1.0 / Hz
    while True:
        N = sleep.time_func()
        yield fn.next()
        D = sleep.time_func() - N
        if (D > T) and strict:
            raise RuntimeError("Cannot support %s Hz. Need: %f, Took: %f."%(Hz, T*1000, D*1000))
        yield T-D


def schedule(_d={}):
    """Schedule factory. Builds a schedule and registers
    some useful handlers.
    """
    if 's' in _d: return _d['s']
    s = Schedule()
    s.register_handler(sleep.SleepHandler())
    s.register_handler(tasks.TasksHandler())
    s.register_handler(nonblock.NonBlockHandler())
    s.register_handler(msg.MessageHandler())
    s.register_handler(tube.TubeHandler())
    _d['s'] = s
    return s


class Schedule(object):
    """The Schedule class implements a round robin scheduler for
    genrator based tasklets.
    """
    def __init__(self):
        self.tasks = []
        self.handlers = set()
        self.type_handlers = {}
        self.register_handler(StopIteratorHandler())

    def register_handler(self, handler, types=[]):
        """Handlers are classes which provide 
        def is_waiting(self): pass
        and
        def handle(self, v, task): pass
        methods. The handle method is called when an instance of the v 
        arg is yielded by a task. The tick method is called at the 
        start of each Schedule().tick() call.
        """
        handler.schedule = self
        for method in getattr(handler, 'exported_functions', []):
            setattr(self, method.__name__, method)
        for type in list(handler.handled_types) + list(types):
            self.type_handlers[type] = handler
        self.handlers.add(handler)

    def install(self, generator, initial_value=None):
        """Installs a generator into the schedule. 
        """
        self.tasks.append((generator, initial_value))

    def run(self):
        while self.tick(): pass

    def tick(self):
        """Iterates the scheduler, running all tasks and calling all 
        handlers.
        """
        active = False
        for handler in self.handlers:
            active = handler.is_waiting() or active
        active = (len(self.tasks) > 0) or active
        tasks = []
        while True:
            try:
                task, send_value = self.tasks.pop(0)
            except IndexError, e:
                break 
            try:
                if isinstance(send_value, Exception):
                    r = task.throw(send_value)
                else:
                    r = task.send(send_value)
            except StopIteration, e:
                r = e
            if r is None: 
                tasks.append((task, None))
            else:
                try:
                    handler = self.type_handlers[type(r)]
                except KeyError:
                    raise RuntimeError("Don't know what to do with yielded type: %s" % type(r))
                handler.handle(r, task)
        self.tasks[:] = tasks
        return active

