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
python-sflib html.py

Author: Marco Pantaleoni
Copyright (C) 2008 Marco Pantaleoni. All rights reserved.

>>> HTML(BODY(TITLE(TEXT('Test'))))
<html>
  <body>
    <title>Test</title>
  </body>
</html>

>>> HTML(HEAD(META(http_equiv="Content-Type", content="text/html; charset=ISO-8859-1")), BODY(TITLE(TEXT('Test'))))
<html>
  <head>
    <meta content="text/html; charset=ISO-8859-1" http-equiv="Content-Type"></meta>
  </head>
  <body>
    <title>Test</title>
  </body>
</html>

>>> COMMENT(TEXT("a comment"))
<!-- a comment -->

>>> table = TABLE(class_='form', id_='mytable')

>>> table
<table id="mytable" class="form">
<BLANKLINE>
</table>

>>> row = TR(TD(TEXT('Name')), TD(TEXT('<input name="Name">'), colspan=2), parent=table, id_='row1')

>>> row
<tr id="row1">
  <td>
    Name
  </td>
  <td colspan="2">
    <input name="Name">
  </td>
</tr>

>>> row = TR(parent=table, id_='row2')

>>> row
<tr id="row2">
<BLANKLINE>
</tr>

>>> row.add(TD(B(TEXT('Last name')))).add(TD(TEXT('<input name="lastname">'), colspan=2))
<tr id="row2">
  <td>
    <b>Last name</b>
  </td>
  <td colspan="2">
    <input name="lastname">
  </td>
</tr>

>>> table
<table id="mytable" class="form">
  <tr id="row1">
    <td>
      Name
    </td>
    <td colspan="2">
      <input name="Name">
    </td>
  </tr>
  <tr id="row2">
    <td>
      <b>Last name</b>
    </td>
    <td colspan="2">
      <input name="lastname">
    </td>
  </tr>
</table>

>>> table.getElementTagName()
'table'

>>> table.getElementId()
'mytable'

>>> table.getElementClass()
'form'

>>> tds = table.getElementsByTagName('td')
>>> len(tds)
4

>>> tds = table.getElementsByTagName('td', recursive=False)
>>> len(tds)
0

>>> table.getElementsWithId('row2')
[<tr id="row2">
  <td>
    <b>Last name</b>
  </td>
  <td colspan="2">
    <input name="lastname">
  </td>
</tr>]

>>> table.getElements('*', 'row2') == table.getElementsWithId('row2')
True

>>> BR()
<br />

>>> A(TEXT("Test site"), href="http://www.test.com")
<a href="http://www.test.com">Test site</a>
"""

# TODO:
#  - indent HTML output

import string

INDENT_AMOUNT = 2

CLASS_ATTRIBUTE      = 'class_'
ID_ATTRIBUTE         = 'id_'
HTTP_EQUIV_ATTRIBUTE = 'http_equiv'

CLASHING_ATTRIBUTES = {
    CLASS_ATTRIBUTE:		'class',
    ID_ATTRIBUTE:		'id',
    HTTP_EQUIV_ATTRIBUTE:	'http-equiv',
    }

#
# HTML_FULL_TAGS element format is
#  (tag_name, default_attributes_dict, options_dict)
#
HTML_FULL_TAGS = (
    ('html', None, {'INLINE': False}),
    ('head', None, {'INLINE': False}),
    ('body', None, {'INLINE': False}),
    'title',
    ('div', None, {'INLINE': False, 'NEWLINE': True}),
    'span',
    'p', 'b', 'i', 'tt', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
    'font', 'blockquote',
    'ul', 'ol', 'li', 'dl', 'dt', 'dd',
    'a', 'map', 'area',
    ('table', None, {'INLINE': False}),
    ('tr', None, {'INLINE': False}),
    ('td', {'colspan': 1, 'rowspan': 1}, {'INLINE': False}),
    ('th', None, {'INLINE': False}),
    'caption',
    'frameset', 'frame', 'base', 'noframes',
    'form', 'input', 'select', 'option', 'textarea',
    'meta', 'style',
    'abbr', 'acronym', 'address', 'base', 'bdo', 'big', 'button',
    'center', 'cite', 'code', 'col', 'colgroup', 'del', 'dfn',
    'em',
    ('fieldset', None, {'INLINE': False}),
    'iframe', 'ins', 'kbd', 'label',
    ('legend', None, {'INLINE': False}),
    'noscript', 'object', 'optgroup', 'pre', 'q', 'samp', 'script',
    'small', 'strong', 'sub', 'tbody', 'tfoot', 'thead', 'var',
    )

HTML_EMPTY_TAGS = (
    ('br', None, {'NEWLINE': True}),
    'hr', 'img', 'link',
    )

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

def filter_out(attrs, defaults):
    res = dict()
    for attr in attrs.keys():
        if (attr in defaults) and (defaults[attr] == attrs[attr]):
            pass
        else:
            res[attr] = attrs[attr]
    return res

def make_html_attrs(attrs):
    html = u''
    for attr in attrs.keys():
        val = attrs[attr]
        if val == True:
            attr_html = u'%s' % attr
        else:
            attr_html = u'%s=\"%s\"' % (attr, attrs[attr])
        html += u' ' + attr_html
    return html

class HTMLEntity(object):
    """
    Base class from which every HTML entity is derived.
    """

    NAME = ''
    DEFAULT_ATTRIBUTES = {}
    OPENCLOSE_TAGS = ()
    INLINE = True
    NEWLINE = False

    def _get_parent(self):
        return self.__parent

    def _set_parent(self, val):
        old_parent = self.__parent
        if old_parent and old_parent != val:
            old_parent.remove(self)
        self.__parent = val
        if self.__parent:
            self.__parent.add(self)
        assert self.__parent == val

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

        parent = None
        if 'parent' in attrs:
            parent = attrs['parent']
            del attrs['parent']
        self.attrs = cvt_pyargs_to_attrs(attrs, defaults = self.DEFAULT_ATTRIBUTES)
        self.children = []
        self.parent = parent
        for arg in args:
            arg.parent = self
            assert arg in self.children

    # -- DOM methods ---------------------------------------------------------

    def getElementTagName(self):
        return self.NAME

    def getElementId(self):
        if 'id' in self.attrs:
            return self.attrs['id']
        return ''

    def getElementClass(self):
        if 'class' in self.attrs:
            return self.attrs['class']
        return ''

    def hasAttribute(self, attributeName):
        return attributeName in self.attrs

    def hasAttributes(self):
        return len(self.attrs.keys()) > 0

    def getAttribute(self, attributeName):
        if attributeName in self.attrs:
            return self.attrs[attributeName]
        return None

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

    # -- END of DOM methods --------------------------------------------------

    def remove(self, child):
        if child in self.children:
            c_prev = child.__prev
            c_next = child.__next
            if c_prev:
                c_prev.__next = c_next
            if c_next:
                c_next.__prev = c_prev
            child.__prev = None
            child.__next = None
            child.__parent = None
            self.children.remove(child)
        return self

    def add(self, child):
        if child not in self.children:
            old_child_parent = child.parent
            if (old_child_parent != self) and (old_child_parent != None):
                old_child_parent.remove(child)
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

    def tag_open(self):
        if len(self.OPENCLOSE_TAGS) >= 1:
            return self.OPENCLOSE_TAGS[0]
        return u''

    def tag_close(self):
        if len(self.OPENCLOSE_TAGS) >= 2:
            return self.OPENCLOSE_TAGS[1]
        return u''

    def _get_html_attrs(self):
        attrs = filter_out(self.attrs, self.DEFAULT_ATTRIBUTES)
        return attrs

    def indent(self, s, level=1):
        indent_base  = u'_' * INDENT_AMOUNT
        indent       = indent_base * level

        lines = s.split('\n')

        indented = []
        for line in lines:
            indented.append(indent + line)
        return string.join(indented, '\n')

    def html(self, do_indent=False, indent_level=0, start_column=0):
        (html, nl) = self._html(do_indent=do_indent, indent_level=indent_level, start_column=start_column)
        return html

    def _html(self, do_indent=False, indent_level=0, start_column=0):
        attrs = self._get_html_attrs()

        tag_open = self.tag_open()
        try:
            tag_close = self.tag_close()
        except:
            tag_close = None

        multiline = False
        nl        = False

        col = start_column
        contents_s = u''

        if tag_close and (not self.INLINE):
            multiline = True
            nl = True

        if self.NEWLINE:
            nl = True

        s_open  = u'<%s%s>' % (tag_open, make_html_attrs(attrs))
        s_close = ''
        if tag_close:
            s_close = u'<%s>' % tag_close

        contents_s = s_open
        col += len(s_open)

        if not tag_close:
            assert (not tag_close)

            inner_contents_s = u''
            for child in self.children:
                (child_s, child_nl) = child._html(do_indent=False, indent_level=0, start_column=0)
                inner_contents_s += child_s
            if inner_contents_s:
                r = u'<%s%s %s />' % (tag_open, make_html_attrs(attrs), unicode(inner_contents_s))
            else:
                r = u'<%s%s />' % (tag_open, make_html_attrs(attrs))
            if nl:
                r = r + '\n'
            #print "[1]RETURNING for (%s, %s, %s): '%s' %s" % (tag_open, indent_level, start_column, r, nl)
            return (r, nl)

        assert tag_close

        if not self.INLINE:
            contents_s += '\n'
            contents_s += ' ' * (start_column + INDENT_AMOUNT)
            col = start_column + INDENT_AMOUNT

        for child in self.children:
            (child_s, child_nl) = child._html(do_indent=True, indent_level=indent_level+1, start_column=col)
            contents_s = contents_s + child_s
            if '\n' in child_s:
                child_rows = child_s.split('\n')
                last_row = None
                if len(child_rows) > 0:
                    last_row = child_rows[-1]
                col = len(last_row)
            else:
                col += len(child_s)
            if child_nl and child.next:
                contents_s += '\n'
                contents_s += ' ' * (start_column + INDENT_AMOUNT)
                col = start_column + INDENT_AMOUNT

        if not self.INLINE:
            contents_s += '\n'
            contents_s += ' ' * start_column
            col = start_column

        contents_s += s_close

        #print "[2]RETURNING for (%s, %s, %s): '%s' %s" % (tag_open, indent_level, start_column, contents_s, nl)
        return (contents_s, nl)

    def __unicode__(self):
        return unicode(self.html())

    def __str__(self):
        return self.html()

    __repr__ = __str__

class TEXT(HTMLEntity):
    """
    A special entity that is used to create plain text into the HTML
    document.
    """

    NAME = 'text'
    DEFAULT_ATTRIBUTES = {}

    def __init__(self, *args, **attrs):
        super(TEXT, self).__init__(**attrs)
        self.contents = args

    def _html(self, do_indent=False, indent_level=0, start_column=0):
        html = u''
        for content in self.contents:
            html += unicode(content)
        return (html, False)

class COMMENT(HTMLEntity):
    """
    A special entity that is used to create HTML comments.
    """

    NAME = 'comment'
    DEFAULT_ATTRIBUTES = {}

    def __init__(self, *args, **attrs):
        super(COMMENT, self).__init__(**attrs)
        self.contents = args

    def _html(self, do_indent=False, indent_level=0, start_column=0):
        html = u'<!-- '
        for content in self.contents:
            html += unicode(content)
        html += u' -->'
        return (html, False)

def _make_html_classes():
    """
    This function creates all the HTML entity classes.
    New classes are created with type(), basing them on HTMLEntity,
    and pushing them into the module namespace.
    """

    global_dict = globals()
    this_mod = __import__(__name__)
    for tag in HTML_FULL_TAGS:
        default_attributes = {}
        opt = {}
        if (type(tag) == type(())) or (type(tag) == type([])):
            if len(tag) >= 3:
                (tag, n_default_attributes, opt) = tag
            elif len(tag) >= 2:
                (tag, n_default_attributes) = tag
            if n_default_attributes != None:
                default_attributes = n_default_attributes
        clsname = tag.upper()
        open_tag  = tag
        close_tag = '/' + tag
        cls_attrs = {'NAME': tag.lower(),
                     'DEFAULT_ATTRIBUTES': default_attributes,
                     'OPENCLOSE_TAGS': (open_tag, close_tag)}
        cls_attrs.update(opt)
        newcls = type(clsname, (HTMLEntity,), cls_attrs)
        this_mod.__dict__[clsname] = newcls
        #setattr(this_mod, clsname, newcls)
        global_dict[clsname] = newcls
    for tag in HTML_EMPTY_TAGS:
        default_attributes = {}
        if (type(tag) == type(())) or (type(tag) == type([])):
            if len(tag) >= 3:
                (tag, n_default_attributes, opt) = tag
            elif len(tag) >= 2:
                (tag, n_default_attributes) = tag
            if n_default_attributes != None:
                default_attributes = n_default_attributes
        clsname = tag.upper()
        open_tag  = tag
        newcls = type(clsname, (HTMLEntity,),
                      {'NAME': tag.lower(),
                       'DEFAULT_ATTRIBUTES': default_attributes,
                       'OPENCLOSE_TAGS': (open_tag, '')})
        this_mod.__dict__[clsname] = newcls
        #setattr(this_mod, clsname, newcls)
        global_dict[clsname] = newcls

_make_html_classes()

def _test():
    import doctest
    doctest.testmod()

if __name__ == '__main__':
    _test()
