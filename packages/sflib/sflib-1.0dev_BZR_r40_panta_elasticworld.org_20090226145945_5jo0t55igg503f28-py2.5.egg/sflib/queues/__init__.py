#!/usr/bin/env python
# ex:ts=4:sw=4:sts=4:et
# -*- tab-width: 4; c-basic-offset: 4; indent-tabs-mode: t -*-
#
# Copyright (C) 2007-2008 Marco Pantaleoni. All rights reserved
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License version 2 as
#    published by the Free Software Foundation.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License along
#    with this program; if not, write to the Free Software Foundation, Inc.,
#    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

"""
python-sflib queue and stack library.

Author: Marco Pantaleoni
Copyright (C) 2007-2008 Marco Pantaleoni. All rights reserved.

FIFO/LIFO data structures (queues and stacks).
"""

import unittest

class Queue:
    """
    Growable queue (FIFO) data structure.
    """

    def __init__(self):
        self.q = []

    def Empty(self):
        if len(self.q) == 0:
            return True
        return False

    def Head(self):
        return self.q[0]

    def Tail(self):
        return self.q[-1]

    def Enqueue(self, item):
        self.q.append(item)

    def Dequeue(self):
        if len(self.q) > 0:
            item = self.q[0]
            del self.q[0]
            return item
        #raise "queue empty"
        raise IndexError            # queue empty

    def __len__(self):
        return len(self.q)

    def __getitem__(self, idx):
        return self.q[idx]

    def __setitem__(self, idx, val):
        self.q[idx] = val

    class q_iterator:
        def __init__(self, q):
            self.q     = q
            self._next = 0

        def __iter__(self):
            return self

        def next(self):
            tail = len(self.q) - 1
            if self._next > tail:
                raise StopIteration
            el = self.q.q[self._next]
            self._next += 1
            return el

    def __iter__(self):
        return Queue.q_iterator(self)

class Stack:
    """
    Growable stack (LIFO) data structure.
    """

    def __init__(self):
        self.l = []

    def Empty(self):
        if len(self.l) == 0:
            return True
        return False

    def Top(self):
        return self.l[-1]

    def Bottom(self):
        return self.l[0]

    def Push(self, item):
        self.l.append(item)

    def Pop(self):
        if len(self.l) > 0:
            item = self.q[-1]
            del self.q[-1]
            return item
        raise "stack empty"

    def __len__(self):
        return len(self.l)

    def __getitem__(self, idx):
        return self.l[idx]

    def __setitem__(self, idx, val):
        self.l[idx] = val

    class s_iterator:
        def __init__(self, s):
            self.l     = s
            self._next = len(self.s) - 1

        def __iter__(self):
            return self

        def next(self):
            if self._next < 0:
                raise StopIteration
            el = self.s.data[self._next]
            self._next -= 1
            return el

    def __iter__(self):
        return Stack.s_iterator(self)
