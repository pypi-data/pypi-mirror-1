#!/usr/bin/env python
# ex:ts=4:sw=4:sts=4:et
# -*- tab-width: 4; c-basic-offset: 4; indent-tabs-mode: t -*-
#
# Copyright (C) 2008 Marco Pantaleoni. All rights reserved
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
python-sflib dictclass.py
"""

class Dictionary(object):
    """
    A base class that acts like a dictionary, but saving to instance
    variables.

       >>> d = Dictionary()

       >>> d['k1'] = 23

       >>> d['k1']
       23

       >>> d.var = 'hello'

       >>> d['var']
       'hello'

       >>> d.getdict()
       {'var': 'hello', 'k1': 23}
    """

    def __getitem__(self, key):
        if hasattr(self, key):
            return getattr(self, key)

    def __setitem__(self, key, val):
        setattr(self, key, val)

    def getdict(self):
        d = dict()
        attrs = self.__dict__
        for k in attrs.keys():
            d[k] = attrs[k]
        return d
