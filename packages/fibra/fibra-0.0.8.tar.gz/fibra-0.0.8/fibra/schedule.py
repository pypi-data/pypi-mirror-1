import plugins.sleep as sleep
import plugins.tasks as tasks
import plugins.nonblock as nonblock
import plugins.msg as msg



class StopIteratorPlugin(object):
    """This is the default plugin for handling StopIteration exceptions.
    It simply ignores the exception, and does not add the task back into 
    the scheduler.
    """
    handled_types = [StopIteration]
    def is_waiting(self): return False
    def handle(self, exception, task): 
        pass


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


def schedule():
    """Schedule factory. Builds a schedule and registers
    some useful plugins."""
    s = Schedule()
    s.register_plugin(sleep.SleepPlugin())
    s.register_plugin(tasks.TasksPlugin())
    s.register_plugin(nonblock.NonBlockPlugin())
    s.register_plugin(msg.MessagePlugin())
    return s


class Schedule(object):
    """The Schedule class implements a round robin scheduler for
    genrator based tasklets.
    """
    def __init__(self):
        self.tasks = []
        self.handlers = {}
        self.plugins = set()
        self.register_plugin(StopIteratorPlugin())
        self.started = False
        self.child_schedules = []

    def register_plugin(self, plugin, types=[]):
        """Plugins are classes which provide 
        def is_waiting(self): pass
        and
        def handle(self, v, task): pass
        methods. The handle method is called when an instance of the v 
        arg is yielded by a task. The tick method is called at the 
        start of each Schedule().tick() call.
        """
        plugin.schedule = self
        for method in getattr(plugin, 'exported_functions', []):
            setattr(self, method.__name__, method)
        for type in list(plugin.handled_types) + list(types):
            self.handlers[type] = plugin
        self.plugins.add(plugin)

    def install(self, generator, initial_value=None):
        """Installs a generator into the schedule. 
        """
        self.tasks.append((generator, initial_value))

    def run(self):
        while self.tick(): pass

    def tick(self):
        """Iterates the scheduler, running all tasks and calling all 
        plugins.
        """
        self.started = True
        active = False
        for plugin in self.plugins:
            active = plugin.is_waiting() or active
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
                    plugin = self.handlers[type(r)]
                except KeyError:
                    raise KeyError('Don\'t know what to do with yielded type: %s' % type(r))
                plugin.handle(r, task)
        self.tasks[:] = tasks
        return active

