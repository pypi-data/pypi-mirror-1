import fibra


def task_a():
    for i in xrange(10):
        yield fibra.SendMsg('AN_EVENT',1,2,3)

def task_b():
    while True:
        msg = yield fibra.RecvMsg('AN_EVENT')
        print 'Received:', msg


def test():
    s = fibra.schedule()
    s.install(task_a())
    s.install(task_b())
    s.run()

if __name__ == "__main__":
    test()
