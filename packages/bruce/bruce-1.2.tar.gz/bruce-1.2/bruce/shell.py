import popen2, select, os

from pygame import event as Event
from pygame import display as Display
import signal
from pygame import locals as L
try:
    import fcntl
except:
    fcntl = None

# !*($&?*($&
O_NONBLOCK = int('04000', 8)

def killprocs(pids, allpids=None):
    if allpids is None:
        allpids = getPids()
    for pid in pids:
        for child in allpids.get(pid, []):
            killprocs([child], allpids)
        try:
            os.kill(pid, 2)
        except:
            pass

def getPids():
    allpids = {}
    while True:
        try:
            lines = os.popen("ps -eo pid,ppid").readlines()
            break
        except IOError:
            continue
    for line in lines:
        if 'PID' in line: continue
        pid, ppid = line.split()
        allpids.setdefault(int(ppid), []).append(int(pid))
    return allpids

class _Spawner:
    def __init__(self):
        self.pids = set()
        # Setup reaper signal
        signal.signal(signal.SIGCHLD, self.reap)

    def reap(self, *signal):
        (pid, status) = os.waitpid(-1, os.WNOHANG)
        if pid:
            if pid in self.pids:
                self.pids.remove(pid)
            #print "reap: self.pids is", self.pids, "removed", pid
        
    def kill(self, pid=None):
        if pid is not None:
            pids = [pid]
        else:
            pids = self.pids
        for p in list(pids): killprocs([p])
        #print "kill: self.pids is", pids

    def spawn(self, command):
        pid = os.fork()
        if pid != 0:
            # parent
            self.pids.add(pid)
            return
        os.execv("/bin/sh", ["sh", "-c", command])

spawner = _Spawner()

class MyInterpreter:
    error = None
    def __init__(self, outputMethod=None):
        # if outputMethod is None, non-interactive
        self.outputMethod = outputMethod
        if fcntl is None:
            raise RuntimeError("Shell not supported - no fcntl module")

    def runsource(self, command, interactive=True):
        stdout, stdin = popen2.popen4(command)
        flags = fcntl.fcntl (stdout, fcntl.F_GETFL, 0)
        flags = flags | O_NONBLOCK
        fcntl.fcntl (stdout, fcntl.F_SETFL, flags)
        #for i in range(10):
        data = ''
        while True:
            try:
                r, w, e = select.select([stdout,], [], [stdout,], 0.1)
            except select.error:
                r, w, e = None, None, None
            if r:
                ndata = stdout.read()
                if not ndata:
                    break
                data += ndata
                print repr(ndata), repr(data)
                while '\n' in data:
                    line, data = data.split('\n', 1)
                    line = line.rstrip()
                    if self.outputMethod is not None:
                        self.outputMethod(line)
                    else: 
                        print "Shell output:", line
            stop = False
            if self.outputMethod is not None or interactive is False:
                for event in Event.get([L.KEYDOWN,]):
                    if event.type == L.KEYDOWN:
                        if event.key == L.K_c and event.mod & L.KMOD_CTRL:
                            stop = True
                            break
                if stop:
                    killprocs([x.pid for x in popen2._active])
                    break
            Display.flip()

if __name__ == "__main__":
    i = MyInterpreter(None)
    print i.runsource('echo hello ; sleep 2 ; echo hello')

