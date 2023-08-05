import os, sys, time
from pyinotify import WatchManager, Notifier, ThreadedNotifier, EventsCodes, ProcessEvent

if len(sys.argv) != 3:
    print "Please run sbin/run"
    raise SystemExit

numServers = int(sys.argv[1])
fcgiEntry = sys.argv[2]

def run(cmd):
    #print cmd
    os.system(cmd)

def kill(pidfile):
    try:
        f = open(pidfile)
        pid = int(f.read())
        run("kill %d 2> /dev/null" % pid)
    except:
        pass

def killProcs():
    run("durus -s --stop 2>/dev/null")
    kill("logs/nginx.pid")
    for i in range(1, numServers + 1):
        kill("logs/fcgi%d.pid" % i)
    run("rm -f logs/*.pid")

Count = 0
class Filter(ProcessEvent):
    def process_default(self, event):
        global Count
        if not (event.name.endswith(".swp") or
                event.name.endswith("~") or
                event.name.startswith(".") or
                event.name.endswith(".pyc") or
                event.path.startswith("html/static/")):
            Count += 1
            ProcessEvent.process_default(self, event)


wm = WatchManager()
mask = EventsCodes.IN_ATTRIB | EventsCodes.IN_CLOSE_WRITE | EventsCodes.IN_CREATE | EventsCodes.IN_DELETE | EventsCodes.IN_DELETE_SELF | EventsCodes.IN_MODIFY | EventsCodes.IN_MOVE_SELF | EventsCodes.IN_MOVED_FROM | EventsCodes.IN_MOVED_TO
wm.add_watch(["conf/", "html/", "src/"], mask, auto_add=True, rec=True)
notifier = Notifier(wm, Filter())

try:
    print ". killing lingering processes"
    while True:
        killProcs()

        run("durus -s --file datastore --logfile logs/durus.log &")
        run("sbin/nginx")
        for i in range(1, numServers + 1):
            run("sbin/spawn-fcgi -f 'python %s' -s tmp/pyflow.socket%d -P logs/fcgi%d.pid" % (fcgiEntry, i, i))

        print ". running"
        
        time.sleep(2)

        while True:
            notifier.process_events()
            if notifier.check_events(None):
                notifier.read_events()
            notifier.process_events()
            if Count > 0:
                print ". restarting"
                time.sleep(.5)
                while notifier.check_events(0):
                    notifier.read_events()
                    notifier.process_events()
                Count = 0
                break

except KeyboardInterrupt:
    print ". shutting down"
    killProcs()
