import fibra

def on_hello():
    msg = yield fibra.RecvMsg('HELLO')
    print "Hello, World"

def send_hello():
    yield fibra.SendMsg('HELLO')

schedule = fibra.schedule()        
schedule.install(on_hello())
schedule.install(send_hello())
schedule.run()


