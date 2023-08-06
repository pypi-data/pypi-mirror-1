"""
The tasks module provides a handler class (TaskHandler) which allows a
tasklet to create other tasklets.

If a tasklet yields a generator object, it is installed into the scheduler
and will run concurrently with the tasklet.

If a tasklet yields a Wait object with a generator object as its argument,
it will install the generator into the scheduler (making it a tasklet) and 
pause its execution and wait until the new tasklet is finished.

If as tasklet yields a Watch object with a generator object as its argument,
it will continue to run until completion and then install the generator into
the scheduler (making it a tasklet).
"""

import types


class Async(object):
    """yield Async(task) to start another task and run it concurrently.
    """
    def __init__(self, task):
        self.task = task


class Watch(object):
    """yield watch(task) to start another task when the current task or
    watching_task is finished.
    """
    def __init__(self, task, watching_task=None):
        self.task = task
        self.watching_task = watching_task


class TasksHandler(object):
    """The task handler allows running tasks to start other tasks by 
    yielding generator, on_finish or spawn objects.
    """
    handled_types = [Watch, Async, StopIteration, types.GeneratorType]
    def __init__(self):
        self.tasks = []
        self.waiting_tasks = {}
        self.handlers = dict((i, getattr(self, "handle_%s" % i.__name__)) for i in self.handled_types)

    def handle(self, new_task, task):
        self.handlers[type(new_task)](new_task, task)

    def handle_StopIteration(self, exception, task):
        try:
            self.tasks.extend(self.waiting_tasks.pop(task))
        except KeyError:
            pass

    def handle_Async(self, event, task):
        self.tasks.extend((event.task, task))

    def handle_Watch(self, watch, task):
        if watch.watching_task is None:
            watching_task = task
        else:
            watching_task = watch.watching_task
        self.waiting_tasks.setdefault(watching_task, []).append(watch.task)
        self.tasks.append(task)

    def handle_generator(self, new_task, task):
        self.waiting_tasks.setdefault(new_task, []).append(task)
        self.tasks.append(new_task) 

    def is_waiting(self): 
        for t in self.tasks:
            self.schedule.install(t)
        self.tasks[:] = []
        return len(self.tasks) > 0 or len(self.waiting_tasks) > 0
