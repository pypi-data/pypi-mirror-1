import fibra
import random
import sys

scheduler = fibra.schedule()

class hackysacker:
    counter = 0
    def __init__(self,name,circle):
        self.name = name
        self.circle = circle
        circle.append(self)
        self.messageQueue = fibra.Tube()
        scheduler.install(self.messageLoop())

    def incrementCounter(self):
        hackysacker.counter += 1
        if hackysacker.counter >= turns:
            while self.circle:
                hs = self.circle.pop()
                if hs is not self:
                    return hs.messageQueue.push('exit')
            sys.exit()

    def messageLoop(self):
        while 1:
            message = yield self.messageQueue.pop()
            if message == "exit":
                debugPrint("%s is going home" % self.name)
                return
            debugPrint("%s got hackeysack from %s" % (self.name, message.name))
            kickTo = self.circle[random.randint(0,len(self.circle)-1)]
            debugPrint("%s kicking hackeysack to %s" % (self.name, kickTo.name))
            yield self.incrementCounter()
            yield kickTo.messageQueue.push(self)
                


def debugPrint(x):
    if debug:
        print x

debug=1
hackysackers=5
turns = 5

def runit(hs=10000,ts=1000,dbg=1):
    global hackysackers,turns,debug
    hackysackers = hs
    turns = ts
    debug = dbg
    
    hackysacker.counter= 0
    circle = []
    one = hackysacker('1',circle)

    for i in range(hackysackers):
        hackysacker(`i`,circle)

    def main():
        yield one.messageQueue.push(one)

    scheduler.install(main())
    scheduler.run()


if __name__ == "__main__":
    import profile
    profile.run("runit(10000, 1000, dbg=0)")

