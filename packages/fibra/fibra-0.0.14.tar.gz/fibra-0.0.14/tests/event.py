import fibra
import fibra.event


class ServerConnection(fibra.event.ServerConnection):
    def recv_message(self, headers, body):
        print headers, body

def connect():
    transport = yield fibra.net.connect(("localhost", 2006))
    client = ServerConnection(transport)
    client.subscribe("hello")
    client.publish("hello", dict(this="header"), "a body is sent too.")
    

def accept_connection(transport):
    """This task will run when a new connection is made."""
    client = Client(transport)
    yield fibra.Async(client.start())


schedule = fibra.schedule()
#this is the task which runs a server
schedule.install(fibra.net.listen(("localhost", 2006), accept_connection))

#this task will run a client
schedule.install(connect())

schedule.run()
    

