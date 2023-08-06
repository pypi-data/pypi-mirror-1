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
visitor.py

A modern implementation of the visitor pattern.

For the details on the original idea, see GoF, p.331:

    "Design Patterns" - Elements of Reusable Object-Oriented Software
    E. Gamma, R. Helm, R. Johnson, J. Vlissides
    Addison Wesley

Example usage:

  >>> class A(Visited):
  ...     def __init__(self, v):
  ...         self.v = v

  >>> class B(Visited):
  ...     def __init__(self, w):
  ...         self.w = w

  >>> class A_operator_emit_HTML(Operator):
  ...     def Perform(self, visited, html_class):
  ...         s = '<strong class="%s">%s</strong>' % (html_class, visited.v)
  ...         return s

  >>> class B_operator_emit_HTML(Operator):
  ...     def Perform(self, visited, html_class):
  ...         s = '<b class="%s">%s</b>' % (html_class, visited.w)
  ...         return s

  >>> operation_emit_html = Operation('emit_HTML')

  >>> a = A(3)
  >>> b = B(7)

  >>> a.Perform(operation_emit_html, html_class='t1')
  '<strong class="t1">3</strong>'

  >>> b.Perform(operation_emit_html, 't2')
  '<b class="t2">7</b>'

  >>> operation_emit_alt_html = Operation('emit_alt_HTML', operation_emit_html)

  >>> class B_operator_emit_alt_HTML(Operator):
  ...     def Perform(self, visited, html_class):
  ...         s = '<p class="%s"><b>%s</b></p>' % (html_class, visited.w)
  ...         return s

  >>> a.Perform(operation_emit_alt_html, html_class='t1')
  '<strong class="t1">3</strong>'

  >>> b.Perform(operation_emit_alt_html, 't2')
  '<p class="t2"><b>7</b></p>'


@author: Marco Pantaleoni
@contact: Marco Pantaleoni <panta@elasticworld.org>
@contact: Marco Pantaleoni <marco.pantaleoni@gmail.com>
@copyright: Copyright (C) 2008 Marco Pantaleoni. All rights reserved.
"""

class Visited(object):
    """
    Base class for the 'visited' objects.

    Derive from this class the objects that need to be operated upon.
    Or simple define the 'Perform' method as below.
    """

    def Perform(self, operation, *op_args, **op_kwargs):
        return operation._perform(self, op_args, op_kwargs)

class OperatorMetaclass(type):
    def __init__(cls, name, bases, dct):
        super(OperatorMetaclass, cls).__init__(name, bases, dct)

        import re
        m = re.match('(.*)_operator_(.*)', name)
        if m:
            (classname, op_name) = m.groups()
            #print "op_name:%s for classname:%s" % (op_name, classname)
            Operation._register_operator(op_name, classname, cls)

class Operator(object):
    """
    The operator class.

    The operation will call the 'Perform' method in this class.
    Derive a class from Operator for each 'operation' for every 'Visited' class.
    """

    __metaclass__ = OperatorMetaclass

    def __init__(self, visited, *args, **kwargs):
        self.visited = visited
        self.args = args
        self.kwargs = kwargs

    def Perform(self, visited, *args, **kwargs):
        raise "abstract"

class OperationMissingError(Exception):
    def __init__(self, op_name, visited_classname, visited = None):
        self.op_name = op_name
        self.visited_classname = visited_classname
        self.visited = visited

    def __str__(self):
        if self.visited:
            return "No operation '%s' for class %s (object:%s)" % (self.op_name, self.visited_classname, self.visited)
        return "No operation '%s' for class %s" % (self.op_name, self.visited_classname)
    __repr__ = __str__

class Operation(object):
    """
    The Operation class.

    This is not intended to be derived.
    Create an instance of this class for each operation.
    """

    operations = {}
    operators = {}

    def __init__(self, op_name, *fallbacks):
        self.op_args   = []
        self.op_kwargs = {}
        self.op_name   = op_name
        self.op_fallbacks = fallbacks

        Operation.operations[op_name] = self

    def _register_operator(cls, op_name, visited_class_name, operator_class):
        #print "registering operator_class:%s for visited_class_name:%s (op:%s)" % (operator_class, visited_class_name, op_name)
        key = "%s#%s" % (op_name, visited_class_name)
        Operation.operators[key] = operator_class
    _register_operator = classmethod(_register_operator)

    def _get_operator(cls, op_name, visited_class_name):
        #print "searching operator for visited_class_name:%s (op:%s)" % (visited_class_name, op_name)
        key = "%s#%s" % (op_name, visited_class_name)
        try:
            operator_class = Operation.operators[key]
        except:
            raise OperationMissingError(op_name, visited_class_name)
        return operator_class
    _get_operator = classmethod(_get_operator)

    def get_operation(cls, op_name):
        if op_name in Operation.operations:
            return Operation.operations[op_name]
        return None
    get_operation = classmethod(get_operation)

    def _perform(self, visited, op_args, op_kwargs):
        klass = visited.__class__
        classname = klass.__name__
        #print "_perform(op_name:%s visited:%s)" % (self.op_name, classname)
        op_proxy_classname = "%s_operator_%s" % (classname, self.op_name)
        op_proxy_class = None
        try:
            #print "op:%s classname:%s" % (self.op_name, classname)
            op_proxy_class = Operation._get_operator(self.op_name, classname)
            #print "  -> %s" % op_proxy_class
        except OperationMissingError, exc:
            for fb in self.op_fallbacks:
                try:
                    #print "try op:%s fb:%s classname:%s" % (fb, fb.op_name, classname)
                    op_proxy_class = Operation._get_operator(fb.op_name, classname)
                    #print "  found -> %s" % op_proxy_class
                    if op_proxy_class:
                        break
                except OperationMissingError, exc:
                    pass
        if op_proxy_class is None:
            raise OperationMissingError(self.op_name, classname, visited)
        op_proxy  = op_proxy_class(visited, *op_args, **op_kwargs)
        op_method = getattr(op_proxy_class, 'Perform')
        if callable(op_method):
            self.op_args = op_args
            self.op_kwargs = op_kwargs
            args = tuple([op_proxy, visited] + list(op_args))
            return op_method(*args, **op_kwargs)

    def __repr__(self):
        return "Operation %s" % self.op_name

def _test():
    import doctest
    doctest.testmod()

if __name__ == '__main__':
    _test()
