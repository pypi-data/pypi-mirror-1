import time
import fibra
import fibra.net

class Connection(fibra.net.Connection):
    count = 0
    def on_connect(self):
        self.send(" ")

    def on_recv(self, msg):
        Connection.count += 1
        self.send(msg)


s = fibra.net.Client(('localhost',2005), Connection)

schedule = fibra.schedule()
schedule.install(s.task())
T = time.time()
try:
    schedule.run()
except:
    pass
print (Connection.count) / (time.time() - T)
