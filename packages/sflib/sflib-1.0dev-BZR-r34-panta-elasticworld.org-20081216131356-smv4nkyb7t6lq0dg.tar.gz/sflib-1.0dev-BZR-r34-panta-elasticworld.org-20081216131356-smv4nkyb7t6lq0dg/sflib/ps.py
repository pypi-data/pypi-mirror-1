"""
Manage Processes and a ProcessList under Linux.

from http://mail.python.org/pipermail/python-list/2006-June/386765.html

  >>> from sflib import ps
  >>> p = ps.ProcessList()
  >>> p.named("emacs") # doctest: +SKIP
  [Process(pid = 20610), Process(pid = 6076), Process(pid = 6113), Process(pid = 6590), Process(pid = 857), Process(pid = 1394), Process(pid = 28974)]

"""

import os
import signal

class Process(object):
    """Represents a process"""
    def __init__(self, pid):
        """Make a new Process object"""
        self.proc = "/proc/%d" % pid
        pid,command,state,parent_pid = file(os.path.join(self.proc, "stat")).read().strip().split()[:4]
        command = command[1:-1]
        self.pid = int(pid)
        self.command = command
        self.state = state
        self.parent_pid = int(parent_pid)
        self.parent = None
        self.children = []
    def kill(self, sig = signal.SIGTERM):
        """Kill this process with SIGTERM by default"""
        os.kill(self.pid, sig)
    def __repr__(self):
        return "Process(pid = %r)" % self.pid
    def getcwd(self):
        """Read the current directory of this process or None for can't"""
        try:
            return os.readlink(os.path.join(self.proc, "cwd"))
        except OSError:
            return None
    
class ProcessList(object):
    """Represents a list of processes"""
    def __init__(self):
        """Read /proc and fill up the process lists"""
        self.by_pid = {}
        self.by_command = {}
        for f in os.listdir("/proc"):
            if f.isdigit():
                process = Process(int(f))
                self.by_pid[process.pid] = process
                self.by_command.setdefault(process.command, []).append(process)
        for process in self.by_pid.values():
            try:
                parent = self.by_pid[process.parent_pid]
                #print "child",process
                #print "parent",parent
                parent.children.append(process)
                process.parent = parent
            except KeyError:
                pass
    def named(self, name):
        """Returns a list of processes with the given name"""
        return self.by_command.get(name, [])
