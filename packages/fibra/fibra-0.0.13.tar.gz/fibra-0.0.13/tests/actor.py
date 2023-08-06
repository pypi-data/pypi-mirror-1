class Actor(object):
    schedule = None
    def __init__(self):
        self._state = self.mode_inactive

    def task(self):
        while True:
            yield self._state()
    
    def start(self):
        self.schedule.install(self._task)

    def set_mode(self, mode):
        fn = getattr(self, 'mode_%s'%mode, None)
        if fn is None: raise ValueError("Invalid mode: %s"%mode)
        self._state = fn

    def mode_inactive(self)
        pass
