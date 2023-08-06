"""This is a package for fibra plugins.

A fibra plugin can be registered to handle values which are yielded from 
running tasklets.

Eg:
>>> import fibra
>>> import fibra.plugins.sleep
>>> s = fibra.Schedule()
>>> sleep_plugin = fibra.plugins.sleep.SleepPlugin()
>>> s.register_plugin(sleep_plugin)

sets up a scheduler with the SleepPlugin installed. To see what types a
SleepPlugin will handle:

>>> print sleep_plugin.handled_types
[<class 'fibra.plugins.sleep.Sleep'>, <type 'int'>, <type 'float'>, <type 'long'>]

To see what extra functions a plugin will add to the scheduler:

>>> print sleep_plugin.exported_functions
[<bound method SleepPlugin.defer of <fibra.plugins.sleep.SleepPlugin object at 0xa13fd0>>]


To create a custom plugin, use the following protocol.

class Plugin(object):
    handled_types = [list_of_handled_types]
    def handle(self, yielded_value, task):
        #do something with the task 
        #but DONT add it back to the scheduler here!
        pass

    def is_waiting(self):
        #add tasks back into the schedule in this function.
        self.schedule.install(task)

"""
