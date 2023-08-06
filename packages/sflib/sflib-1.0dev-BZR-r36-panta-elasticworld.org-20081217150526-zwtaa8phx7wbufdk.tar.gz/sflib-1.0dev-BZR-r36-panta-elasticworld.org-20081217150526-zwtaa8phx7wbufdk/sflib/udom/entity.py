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
entity.py

Author: Marco Pantaleoni
Copyright (C) 2008 Marco Pantaleoni. All rights reserved.

microDOM library.
"""

CLASS_ATTRIBUTE      = 'class_'
ID_ATTRIBUTE         = 'id_'
HTTP_EQUIV_ATTRIBUTE = 'http_equiv'

CLASHING_ATTRIBUTES = {
    CLASS_ATTRIBUTE:		'class',
    ID_ATTRIBUTE:		'id',
    HTTP_EQUIV_ATTRIBUTE:	'http-equiv',
    }

def cvt_py_arg_to_attr(pyarg):
    if pyarg in CLASHING_ATTRIBUTES:
        return CLASHING_ATTRIBUTES[pyarg]
    return pyarg

def cvt_pyargs_to_attrs(pyargs, defaults={}):
    attrs = dict()
    for k in defaults.keys():
        attrs[k] = defaults[k]
    for pyarg in pyargs.keys():
        attr = cvt_py_arg_to_attr(pyarg)
        val  = pyargs[pyarg]
        attrs[attr] = val
    return attrs

class EntityMetaclass(type):
    def __init__(cls, name, bases, dct):
        super(EntityMetaclass, cls).__init__(name, bases, dct)

        cls._registered[name] = cls

class Entity(object):
    __metaclass__ = EntityMetaclass

    NAME = ''
    DEFAULT_ATTRIBUTES = {}

    _registered = {}

    def _get_parent(self):
        return self.__parent

    def _set_parent(self, val):
        old_parent = self.__parent
        if (old_parent is not None) and (old_parent is not val):
            old_parent.removeChild(self)
        if self.__parent is not None:
            self.__parent.appendChild(self)
        else:
            self.__parent = val
        assert self.__parent is val

    parent = property(_get_parent, _set_parent, None, "parent of this entity")

    def _get_prev(self):
        return self.__prev

    prev = property(_get_prev, None, None, "previous sibling")

    def _get_next(self):
        return self.__next

    next = property(_get_next, None, None, "next sibling")

    def __init__(self, *args, **attrs):
        self.__parent = None
        self.__prev   = None
        self.__next   = None
        self.children = []

        parent = None
        if 'parent' in attrs:
            parent = attrs['parent']
            del attrs['parent']
        self.attrs = cvt_pyargs_to_attrs(attrs, defaults = self.DEFAULT_ATTRIBUTES)
        self.parent = parent
        for arg in args:
            if isinstance(arg, Entity):
                self.appendChild(arg)
                #arg.parent = self
                assert arg in self.children

    # -- DOM methods ---------------------------------------------------------

    def getElementTagName(self):
        return self.NAME

    def getElementType(self):
        return self.getElementTagName()

    def getElementId(self, default=''):
        if 'id' in self.attrs:
            return self.attrs['id']
        return default

    def getElementClass(self, default=''):
        if 'class' in self.attrs:
            return self.attrs['class']
        return default

    def hasAttribute(self, attributeName):
        return attributeName in self.attrs

    def hasAttributes(self):
        return len(self.attrs.keys()) > 0

    def getAttribute(self, attributeName, default=None):
        if attributeName in self.attrs:
            return self.attrs[attributeName]
        return default

    def setAttribute(self, attributeName, value):
        self.attrs[attributeName] = value
        return self

    def getRoot(self):
        p = self.parent
        if p:
            return p.getRoot()
        return self

    def getElementsByTagName(self, tagName, recursive=True):
        tagName = tagName.lower()
        elements = []
        for child in self.children:
            if (tagName == '*') or (tagName == child.getElementTagName().lower()):
                elements.append(child)
            if recursive:
                child_elements = child.getElementsByTagName(tagName, recursive)
                elements = elements + child_elements
        return elements

    def getElementsWithId(self, elementId, recursive=True):
        elementId = elementId.lower()
        elements = []
        for child in self.children:
            if (elementId == '*') or (elementId == child.getElementId().lower()):
                elements.append(child)
            if recursive:
                child_elements = child.getElementsWithId(elementId, recursive)
                elements = elements + child_elements
        return elements

    def getElementWithId(self, elementId, recursive=True):
        elementId = elementId.lower()
        for child in self.children:
            if (elementId == '*') or (elementId == child.getElementId().lower()):
                return child
            if recursive:
                r = child.getElementWithId(elementId, recursive)
                if r:
                    return r
        return None

    def getElements(self, tagName='*', elementId='*', elementClass='*', recursive=True):
        tagName = tagName.lower()
        elementId = elementId.lower()
        elementClass = elementClass.lower()
        elements = []
        for child in self.children:
            if (tagName == '*') or (tagName == child.getElementTagName().lower()):
                if (((elementId == '*') or (elementId == child.getElementId().lower())) and
                    ((elementClass == '*') or (elementClass == child.getElementClass().lower()))):
                    elements.append(child)
            if recursive:
                child_elements = child.getElements(tagName, elementId, elementClass, recursive)
                elements = elements + child_elements
        return elements

    def find(self, test_function, max_depth=0, depth=0):
        """Returns a list of descendants that pass the test function."""
        elements = []
        for child in self.children:
            if test_function(child):
                elements.append(child)
            if (max_depth <= 0) or (depth + 1 < max_depth):
                elements += child.find(test_function, max_depth, depth+1)
        return elements

    # -- END of DOM methods --------------------------------------------------

    def insertChild(self, position, child):
        if child in self.children:
            return self

        assert not (child in self.children)

        l = len(self.children)
        if position < 0:
            position = position % l
        if position >= l:
            return self.appendChild(child)

        c_parent = child.parent
        if (c_parent is not self) and (c_parent is not None):
            c_parent.removeChild(child)

        assert l > 0
        assert position >= 0
        assert position < l

        cur = self.children[position]
        cur_p = cur.__prev

        child.__prev   = cur_p
        child.__next   = cur
        child.__parent = self
        cur.__prev     = child
        if cur_p is not None:
            cur_p.__next = child
        self.children.insert(position, child)
        return self

    def appendChild(self, child):
        if child in self.children:
            return self

        assert not (child in self.children)

        c_parent = child.parent
        if (c_parent is not self) and (c_parent is not None):
            c_parent.removeChild(child)

        last_child = None
        if len(self.children) > 0:
            last_child = self.children[-1]
        if last_child:
            last_child.__next = child
        child.__prev = last_child
        child.__next = None
        child.__parent = self
        self.children.append(child)
        return self

    def replaceChild(self, oldChild, newChild):
        assert oldChild in self.children
        position = self.children.index(oldChild)
        self.removeChild(oldChild)
        self.insertChild(position, newChild)
        return self

    def removeChild(self, child):
        if not child in self.children:
            return self
        assert child in self.children

        c_prev = child.__prev
        c_next = child.__next
        if c_prev is not None:
            c_prev.__next = c_next
        if c_next is not None:
            c_next.__prev = c_prev
        child.__prev   = None
        child.__next   = None
        child.__parent = None
        self.children.remove(child)
        return self

    # the following 'Perform' method implements the interface for
    # the visitor pattern protocol provided by sflib.visitor
    def Perform(self, operation, *op_args, **op_kwargs):
        return operation._perform(self, op_args, op_kwargs)

    def visit(self, visit_function, max_depth=0, depth=0):
        r = visit_function(self)
        r_child = []
        if (max_depth <= 0) or (depth + 1 < max_depth):
            for child in self.children:
                r_child.append(child.visit(visit_function, max_depth, depth+1))
        return (r, r_child)

    def getClassByTagName(cls, tagname):
        if tagname in cls._registered:
            return cls._registered[tagname]
        return None
    getClassByTagName = classmethod(getClassByTagName)

    def createElement(self, tagname, *args, **kwargs):
        el_class = self.getClassByTagName(tagname)
        el = el_class(*args, **kwargs)
        self.appendChild(el)
        return el

    def __repr__(self):
        attr_r = ""
        for k, v in self.attrs.items():
            attr_r += " %s=%s" % (k, repr(v))
        tagName = self.getElementTagName()
        children_r = ""
        for child in self.children:
            child_r = child
            #child_r = unicode(child)
            #child_r = child_r.encode('ascii', 'replace')
            #children_r += repr(child)
            children_r += repr(child_r)
        r = "<%s%s>%s</%s>" % (tagName, attr_r, children_r, tagName)
        return r

def _test():
    import doctest
    doctest.testmod()

if __name__ == '__main__':
    _test()
