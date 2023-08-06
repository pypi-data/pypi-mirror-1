#!/usr/bin/env python
# ex:ts=8:sw=4:sts=4:et
# -*- tab-width: 8; c-basic-offset: 4; indent-tabs-mode: t -*-
#
# Original:
#   http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/278731
# see also:
#   http://www.noah.org/wiki/Daemonize_Python
#
# Parts from the djangocerise version by Loic d'Anterroches,
# downloaded from:
#   http://xhtml.net/documents/scripts/djangocerise-1.2.zip
# (http://xhtml.net/scripts/Django-CherryPy-server-DjangoCerise)
# which is based on Juergen Hermanns
# http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/66012
# downloaded from: http://homepage.hispeed.ch/py430/python/daemon.py
#
# Changes to the originals are:
# Copyright (C) 2008-2009 Marco Pantaleoni. All rights reserved

"""daemonize python library

Configurable daemon behaviors:

   1.) The current working directory set to the "/" directory.
   2.) The current file creation mode mask set to 0.
   3.) Close all open files (1024). 
   4.) Redirect standard I/O streams to "/dev/null".

A failed call to fork() now raises an exception.

References:
   1) Advanced Programming in the Unix Environment: W. Richard Stevens
   2) Unix Programming Frequently Asked Questions:
         http://www.erlenstar.demon.co.uk/unix/faq_toc.html

@see: http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/278731
@see: http://www.noah.org/wiki/Daemonize_Python
@see: http://xhtml.net/documents/scripts/djangocerise-1.2.zip
@see: http://xhtml.net/scripts/Django-CherryPy-server-DjangoCerise
@see: http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/66012
@see: http://homepage.hispeed.ch/py430/python/daemon.py

@author: Chad J. Schroeder
@copyright: Copyright (C) 2005 Chad J. Schroeder
"""

__author__ = "Chad J. Schroeder"
__copyright__ = "Copyright (C) 2005 Chad J. Schroeder"

__revision__ = "$Id$"
__version__ = "0.2"

__contributors__ = [
    "Marco Pantaleoni <panta@elasticworld.org>",
]

# Standard Python modules.
import os               # Miscellaneous OS interfaces.
import sys              # System-specific parameters and functions.
import pwd

from sflib import lockfile as lfile

# Default daemon parameters.
# File mode creation mask of the daemon.
UMASK = 0

# Default working directory for the daemon.
WORKDIR = "/"

# Default maximum for the number of available file descriptors.
MAXFD = 1024

# The standard I/O file descriptors are redirected to /dev/null by default.
if (hasattr(os, "devnull")):
    REDIRECT_TO = os.devnull
else:
    REDIRECT_TO = "/dev/null"

def change_uid_gid(uid, gid=None):
    """Try to change UID and GID to the provided values.
    UID and GID are given as names like 'nobody' not integer.

    Src: http://mail.mems-exchange.org/durusmail/quixote-users/4940/1/
    """
    if not uid:
        return
    if not ((os.geteuid() == 0) or (os.getuid() == 0)):
        # Do not try to change the gid/uid if not root.
        return
    (uid, gid) = get_uid_gid(uid, gid)
    os.setgid(gid)
    os.setuid(uid)

def get_uid_gid(uid, gid=None):
    """Try to get the UID and GID numeric values corresponding to
    the provided symbolic ones.

    Src: http://mail.mems-exchange.org/durusmail/quixote-users/4940/1/
    """
    import pwd, grp

    default_grp = None
    if uid:
        uid, default_grp = pwd.getpwnam(uid)[2:4]
    if not gid:
        gid = default_grp
    else:
        assert gid is not None
        assert gid != ''
        try:
            gid = grp.getgrnam(gid)[2]            
        except KeyError:
            gid = default_grp
    return (uid, gid)

def chown_files(filenames, uid, gid=None):
    if not ((os.geteuid() == 0) or (os.getuid() == 0)):
        # Do not try to change the gid/uid if not root.
        return
    (uid, gid) = get_uid_gid(uid, gid)
    if uid or gid:
        for filename in filenames:
            if os.path.exists(filename):
                os.chown(filename, uid, gid)

#def chown_pid_log(uid, gid=None):
#    global options
#    chown_files([options.PIDFILE, options.LOGFILE])

def log_info(log, msg):
    if log is not None:
        log.info(msg)

def log_debug(log, msg):
    if log is not None:
        log.debug(msg)

class RedirectedFileStub(object):
    """
    A file-like duck-typed class, used to replace sys.stderr and sys.stdout,
    making them point to a logging object.
    """

    def __init__(self, log):
        self.log = log

    def flush(self):
        pass

    def close(self):
        pass

    def write(self, text):
        if text and text[-1] == '\n':
            text = text[:-1]
        self.log.debug(text)

def daemonize(pidfile = None, lockfile = None,
              run_as_user = None, run_as_group = None,
              workdir = WORKDIR, umask = UMASK,
              redirect_to = REDIRECT_TO, maxfd = MAXFD,
              files_for_child = [],
              log = None,
              loggers = None,
              stdout_log = None, stderr_log = None):
    """
    Detach a process from the controlling terminal and run it in the
    background as a daemon.
    """

    log_info(log, "Daemonizing...")

    # already a daemon? return now
    if os.getppid() == 1:
        log_debug(log, "already a daemon. Returning.")
        return True

    # create the lockfile as the current user
    locked = False
    if lockfile:
        locked = lfile.get_lock(lockfile)
        if not locked:
            #log_debug(log, "can't obtain a lock. Returning.")
            sys.stderr.write("can't obtain a lock ('%s' exists).\n" % lockfile)
            sys.exit(1)
            return False

#    # drop user if 'run_as' is specified, and we were run as root
#    if ((os.getuid() == 0) or (os.geteuid() == 0) and (run_as is not None) and run_as):
#        if run_as != None:
#            pw = pwd.getpwnam(run_as)
#            os.setuid(pw[2])		# pw[2] is pw_uid

    # do the UNIX double-fork magic, see Stevens' "Advanced
    # Programming in the UNIX Environment" for details (ISBN 0201563177)

    try:
        # Fork a child process so the parent can exit.  This returns control to
        # the command-line or shell.  It also guarantees that the child will not
        # be a process group leader, since the child receives a new process ID
        # and inherits the parent's process group ID.  This step is required
        # to insure that the next call to os.setsid is successful.
        #log_debug(log, "first fork()")
        pid = os.fork()
    except OSError, e:
        raise Exception, "%s [%d]" % (e.strerror, e.errno)

    if pid > 0:
        # we have our first child
        assert pid != 0
        #log_debug(log, "first child obtained. Exiting.")
        # exit() or _exit()?
        # _exit is like exit(), but it doesn't call any functions registered
        # with atexit (and on_exit) or any registered signal handlers.  It also
        # closes any open file descriptors.  Using exit() may cause all stdio
        # streams to be flushed twice and any temporary files may be unexpectedly
        # removed.  It's therefore recommended that child branches of a fork()
        # and the parent branch(es) of a daemon use _exit().
        os._exit(0)	# Exit parent of the first child.

    # the first child.
    assert pid == 0
    #log_debug(log, "in first child.")

    # To become the session leader of this new session and the process group
    # leader of the new process group, we call os.setsid().  The process is
    # also guaranteed not to have a controlling terminal.
    os.setsid()

    # Is ignoring SIGHUP necessary?
    #
    # It's often suggested that the SIGHUP signal should be ignored before
    # the second fork to avoid premature termination of the process.  The
    # reason is that when the first child terminates, all processes, e.g.
    # the second child, in the orphaned group will be sent a SIGHUP.
    #
    # "However, as part of the session management system, there are exactly
    # two cases where SIGHUP is sent on the death of a process:
    #
    #   1) When the process that dies is the session leader of a session that
    #      is attached to a terminal device, SIGHUP is sent to all processes
    #      in the foreground process group of that terminal device.
    #   2) When the death of a process causes a process group to become
    #      orphaned, and one or more processes in the orphaned group are
    #      stopped, then SIGHUP and SIGCONT are sent to all members of the
    #      orphaned group." [2]
    #
    # The first case can be ignored since the child is guaranteed not to have
    # a controlling terminal.  The second case isn't so easy to dismiss.
    # The process group is orphaned when the first child terminates and
    # POSIX.1 requires that every STOPPED process in an orphaned process
    # group be sent a SIGHUP signal followed by a SIGCONT signal.  Since the
    # second child is not STOPPED though, we can safely forego ignoring the
    # SIGHUP signal.  In any case, there are no ill-effects if it is ignored.
    #
    # import signal           # Set handlers for asynchronous events.
    # signal.signal(signal.SIGHUP, signal.SIG_IGN)

    try:
        # Fork a second child and exit immediately to prevent zombies.  This
        # causes the second child process to be orphaned, making the init
        # process responsible for its cleanup.  And, since the first child is
        # a session leader without a controlling terminal, it's possible for
        # it to acquire one by opening a terminal in the future (System V-
        # based systems).  This second fork guarantees that the child is no
        # longer a session leader, preventing the daemon from ever acquiring
        # a controlling terminal.
        #log_debug(log, "second fork()")
        pid = os.fork()	# Fork a second child.
    except OSError, e:
        raise Exception, "%s [%d]" % (e.strerror, e.errno)

    if pid > 0:
        # the first child has a child
        assert pid > 0

        #log_debug(log, "the first child has a child.")

        # write child PID into lockfile
        if locked:
            fh = open(lockfile, "w")
            fh.write("%d\n" % pid)
            fh.close()
    
        fh = open(pidfile, "w")
        fh.write("%d\n" % pid)
        fh.close()

        if (run_as_user or run_as_group):
            chown_files([pidfile, lockfile] + list(files_for_child),
                        run_as_user, run_as_group)

        #log_debug(log, "Exiting first child.")
        # exit() or _exit()?  See below.
        os._exit(0)	# Exit parent (the first child) of the second child.

    # the second child
    assert pid == 0
    #log_debug(log, "in second child.")

    # Since the current working directory may be a mounted filesystem, we
    # avoid the issue of not being able to unmount the filesystem at
    # shutdown time by changing it to the root directory.
    os.chdir(workdir)
    # We probably don't want the file mode creation mask inherited from
    # the parent, so we give the child complete control over permissions.
    os.umask(umask)

    # Close all open file descriptors.  This prevents the child from keeping
    # open any file descriptors inherited from the parent.  There is a variety
    # of methods to accomplish this task.  Three are listed below.
    #
    # Try the system configuration variable, SC_OPEN_MAX, to obtain the maximum
    # number of open file descriptors to close.  If it doesn't exists, use
    # the default value (configurable).
    #
    # try:
    #    l_maxfd = os.sysconf("SC_OPEN_MAX")
    # except (AttributeError, ValueError):
    #    l_maxfd = maxfd
    #
    # OR
    #
    # if (os.sysconf_names.has_key("SC_OPEN_MAX")):
    #    l_maxfd = os.sysconf("SC_OPEN_MAX")
    # else:
    #    l_maxfd = maxfd
    #
    # OR
    #
    # Use the getrlimit method to retrieve the maximum file descriptor number
    # that can be opened by this process.  If there is not limit on the
    # resource, use the default value.
    #
    import resource		# Resource usage information.
    l_maxfd = resource.getrlimit(resource.RLIMIT_NOFILE)[1]
    if (l_maxfd == resource.RLIM_INFINITY):
        l_maxfd = maxfd

    log_fds = []
    for logger in loggers:
        _log = logger
        while _log is not None:
            #print "LOG %s" % _log
            import logging
            assert isinstance(_log, logging.Logger)
            for hdlr in _log.handlers:
                #print "LOG HDLR %s" % hdlr
                if isinstance(hdlr, logging.StreamHandler):
                    #print "LOG STREAM HDLR %s" % hdlr
                    assert isinstance(hdlr, logging.StreamHandler)
                    fd = hdlr.stream.fileno()
                    if fd not in log_fds:
                        log_fds.append(fd)
            _log = _log.parent

    if stdout_log is not None:
        sys.stdout = RedirectedFileStub(stdout_log)
    if stderr_log is not None:
        sys.stderr = RedirectedFileStub(stderr_log)

    # Iterate through and close all file descriptors.
    for fd in range(0, l_maxfd):
        try:
            if fd not in log_fds:
                #log_debug(log, "close(%s)" % fd)
                os.close(fd)
            else:
                log_debug(log, "skipping close(%s)" % fd)
        except OSError:	# ERROR, fd wasn't open to begin with (ignored)
            pass

    # Redirect the standard I/O file descriptors to the specified file.  Since
    # the daemon has no controlling terminal, most daemons redirect stdin,
    # stdout, and stderr to /dev/null.  This is done to prevent side-effects
    # from reads and writes to the standard I/O file descriptors.

    # This call to open is guaranteed to return the lowest file descriptor,
    # which will be 0 (stdin), since it was closed above.
    os.open(redirect_to, os.O_RDWR)	# standard input (0)

    # Duplicate standard input to standard output and standard error.
    os.dup2(0, 1)			# standard output (1)
    os.dup2(0, 2)			# standard error (2)

#    # write child PID into lockfile
#    if locked:
#        fh = open(lockfile, "w")
#        fh.write("%d\n" % os.getpid())
#        fh.close()
#
#    fh = open(pidfile, "w")
#    fh.write("%d\n" % os.getpid())
#    fh.close()

    # drop privileges
    if run_as_user or run_as_group:
        change_uid_gid(run_as_user, run_as_group)
    #log_debug(log, "returning from child.")

    return True

if __name__ == "__main__":

    if not daemonize():
        sys.exit(1)

    # The code, as is, will create a new file in the root directory, when
    # executed with superuser privileges.  The file will contain the following
    # daemon related process parameters: return code, process ID, parent
    # process group ID, session ID, user ID, effective user ID, real group ID,
    # and the effective group ID.  Notice the relationship between the daemon's 
    # process ID, process group ID, and its parent's process ID.

    procParams = """
               return code = %s
               process ID = %s
               parent process ID = %s
               process group ID = %s
               session ID = %s
               user ID = %s
               effective user ID = %s
               real group ID = %s
               effective group ID = %s
               """ % (retCode, os.getpid(), os.getppid(), os.getpgrp(), os.getsid(0),
                      os.getuid(), os.geteuid(), os.getgid(), os.getegid())

    open("daemonize.log", "w").write(procParams + "\n")

    sys.exit(retCode)
