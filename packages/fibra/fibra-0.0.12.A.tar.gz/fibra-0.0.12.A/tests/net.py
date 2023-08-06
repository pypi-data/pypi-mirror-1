import fibra
import fibra.net

class Connection(fibra.net.Connection):
    def on_connect(self):
        self.send("hello.")

    def on_recv(self, msg):
        self.send(msg)

    def on_close(self):
        print self, 'closed.'

s = fibra.net.Server(('localhost',2005), Connection)

schedule = fibra.schedule()
schedule.install(s.task())
schedule.run()
