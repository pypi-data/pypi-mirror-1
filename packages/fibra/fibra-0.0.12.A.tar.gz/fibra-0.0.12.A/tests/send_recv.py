import fibra

SIMPLE_MESSAGE_TYPE = 1

def task_a():
    for i in xrange(10):
        yield fibra.Send(SIMPLE_MESSAGE_TYPE, ('A', 'Message', i))

def task_b():
    while True:
        msg = yield fibra.Recv(SIMPLE_MESSAGE_TYPE)
        print 'Received:', msg

def test():
    s = fibra.schedule()
    s.install(task_a())
    s.install(task_b())
    s.run()

if __name__ == "__main__":
    test()
