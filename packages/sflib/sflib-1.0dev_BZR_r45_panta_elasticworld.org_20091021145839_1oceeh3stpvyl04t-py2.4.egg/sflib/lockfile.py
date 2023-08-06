#!/usr/bin/env python
# ex:ts=8:sw=4:sts=4:et
# -*- tab-width: 8; c-basic-offset: 4; indent-tabs-mode: t -*-
#
# inspired by:
#   http://www.velocityreviews.com/forums/t359733-how-to-lock-files-the-easiestbest-way.html
# Original is:
# Copyright (C) Jim Segrave
#
# Changes to the original are:
# Copyright (C) 2008 Marco Pantaleoni. All rights reserved

__author__ = "Jim Segrave"
__copyright__ = "Copyright (C) Jim Segrave"

__revision__ = "$Id$"
__version__ = "0.1"

__contributors__ = [
   "Marco Pantaleoni <panta@elasticworld.org>",
]

import os
import errno
import sys
import time
import stat

# the maximum reasonable time for a process to be
MAX_WAIT = 10

def get_lock(lockfile, max_wait = 0):
    lockdir = os.path.dirname(lockfile)
    if not os.path.exists(lockdir):
        os.mkdir(lockdir, 0777)

    while True:
        try:
            fd = os.open(lockfile, os.O_EXCL | os.O_RDWR | os.O_CREAT)
            # we created the lockfile, so we're the owner
            break
        except OSError, e:
            if e.errno != errno.EEXIST:
                # should not occur
                raise
     
        try:
            # the lock file exists, try to stat it to get its age
            # and read it's contents to report the owner PID
            f = open(lockfile, "r")
            s = os.stat(lockfile)
        except OSError, e:
            if e.errno != errno.EEXIST:
                #sys.exit("%s exists but stat() failed: %s" % (lockfile, e.strerror))
                sys.stderr.write("%s exists but stat() failed: %s\n" % (lockfile, e.strerror))
                # we didn't create the lockfile, so it did exist, but it's gone now.
                # Just try again
                continue
     
        # we didn't create the lockfile and it's still there, check its age
        if (max_wait is not None) and (max_wait > 0):
            now = int(time.time())
            if now - s[stat.ST_MTIME] > max_wait:
                pid = f.readline()
                sys.stderr.write("%s has been locked for more than %d seconds (PID %s)\n" % (lockfile, max_wait, pid))
                #sys.exit("%s has been locked for more than %d seconds (PID %s)" % (lockfile, max_wait, pid))
                return False

            # it's not been locked too long, wait a while and retry
            f.close()
            time.sleep(1)
            continue
        else:
            pid = f.readline()
            sys.stderr.write("%s is locked by PID %s\n" % (lockfile, pid))
            return False

    # if we get here. we have the lockfile. Convert the os.open file
    # descriptor into a Python file object and record our PID in it
     
    f = os.fdopen(fd, "w")
    f.write("%d\n" % os.getpid())
    f.close()
    return True
