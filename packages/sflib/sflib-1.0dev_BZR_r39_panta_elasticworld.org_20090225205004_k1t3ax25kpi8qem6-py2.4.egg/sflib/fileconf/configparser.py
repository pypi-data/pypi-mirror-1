#!/usr/bin/env python
# ex:ts=8:sw=4:sts=4:et
# -*- tab-width: 8; c-basic-offset: 4; indent-tabs-mode: t -*-
#
# Copyright (C) 2008 Marco Pantaleoni. All rights reserved

"""
"""

import re

from config import *

class ConfigFileError(Exception):
    """A config file error exception."""

    def __init__(self, msg, line, pathname = None):
        self.msg      = msg
        self.line     = line
        self.pathname = pathname
        super(ConfigFileError, self).__init__(msg)

    def __str__(self):
        if self.pathname:
            return "%s (line:%s file:%s)" % (self.msg, self.line, repr(self.pathname))
        return "%s (line:%s)" % (self.msg, self.line)

class SyntaxError(ConfigFileError):
    """A config file syntax error exception."""

class SemanticError(ConfigFileError):
    """A config file semantic error exception."""

def textrepr(value):
    if value is None:
        return ''
    return str(value)

class TokenParser(object):
    def __init__(self, fh, pathname = None, context = None):
        self.fh       = fh
        self.pathname = pathname
        self.lnum     = 0
        self.parsed   = None

        self.context  = context

    def _perform_var_subst(self, text):
        while True:
            m = re.match(r'.*?\$\{([a-zA-Z0-9_.]+)\}.*', text)
            if not m:
                break
            varname  = m.group(1)
            varvalue = textrepr(self.context.get(varname))
            text = re.sub(r'\$\{' + re.escape(varname) + r'\}', varvalue, text)
        return text

    def _perform_cmd_subst(self, text):
        import os

        cmd = self._perform_var_subst(text)
        fh = os.popen(cmd, 'r')
        contents = fh.read()
        contents = contents.strip()
        fh.close()
        return contents

    def Tokenize(self):
        stack = []
        level = 0

        stack.append([])

        while True:
            line = self.fh.readline()
            self.lnum += 1
            if (line is None) or (line == ''):
                self.parsed = None
                if (level > 0):
                    raise SyntaxError("closing parenthesis is missing", self.lnum, self.pathname)
                return None             # EOF
            if line == '\n':
                continue                # skip empty lines

            while line:
                #print "L%s line:'%s'\n\tstack:%s sl:%s" % (level, line.rstrip(), stack, len(stack))
                while (len(line) > 0) and (line[0] in (' ', '\t',)):
                    line = line[1:]
                if line == '\n':
                    #print "[*] L%s line:'%s'\n\tstack:%s sl:%s" % (level, line.rstrip(), stack, len(stack))
                    if len(stack) == 1:
                        self.parsed = stack.pop()
                        return self.parsed

                line = line.lstrip()

                if line == '':
                    break

                if line.startswith('('):
                    level += 1
                    stack.append([])
                    line = line[1:]
                elif line.startswith(')'):
                    level -= 1
                    closed = stack.pop()
                    if (level < 0) and (len(stack) != 1):
                        raise SyntaxError("parentheses don't match", self.lnum, self.pathname)
                    stack[-1] = stack[-1] + [ closed ]
                    line = line[1:]
                    if level == 0:
                        if len(stack) != 1:
                            raise SyntaxError("parentheses don't match", self.lnum, self.pathname)
                        #print "ST:%s" % stack
                        #self.parsed = stack.pop()[0]
                        self.parsed = stack.pop()
                        return self.parsed
                elif line.startswith('"'):
                    close_at = line[1:].index('"')
                    val = self._perform_var_subst(line[1:close_at+1])
                    stack[-1] = stack[-1] + [val]
                    line = line[close_at+2:]
                elif line.startswith("'"):
                    close_at = line[1:].index("'")
                    val = self._perform_var_subst(line[1:close_at+1])
                    stack[-1] = stack[-1] + [val]
                    line = line[close_at+2:]
                elif line.startswith("`"):
                    close_at = line[1:].index("`")
                    val = self._perform_cmd_subst(line[1:close_at+1])
                    stack[-1] = stack[-1] + [val]
                    line = line[close_at+2:]
                elif line[0].isdigit():
                    s = ""
                    while line and (line[0].isdigit() or (line[0] in ('+', '-', '.'))):
                        s = s + line[0]
                        line = line[1:]
                    if '.' in s:
                        val = float(s)
                    else:
                        val = int(s)
                    stack[-1] = stack[-1] + [val]
                elif line.startswith('#'):
                    break
                else:
                    s = ""
                    while line and not (line[0].isspace() or (line[0] in ('(', ')', '#'))):
                        s = s + line[0]
                        line = line[1:]
                    stack[-1] = stack[-1] + [ s ]
            # -- END OF INTERNAL LINE PARSING CYCLE --
        # -- END OF LINE I/O CYCLE

        if len(stack) != 1:
            raise SyntaxError("parentheses don't match", self.lnum, self.pathname)
        #self.parsed = stack.pop()[0]
        self.parsed = stack.pop()
        return self.parsed

class ConfigParser(object):
    """
    The main class of this module.

    Use like:

      cp = ConfigParser(config_pathname)
      cnf = cp.Load()

    The cnf object returned will be a sflib.fileconf.config.Config instance
    """

    def __init__(self, pathname, cnf = None):
        self.pathname = pathname
        self.cnf      = cnf
        self.fh       = None

    def HandleGenericSyntax(self, tokens):
        """Override this method in derived classes to implement specific semantics."""
        print "unrecognized syntax '%s' (line %s)" % (tokens, self.tparser.lnum)
        return self

    def HandleInclude(self, tokens):
        # INCLUDE form
        cp = ConfigParser(tokens[1], self.cnf)
        cp.Load()
        return self

    def HandleAssignment(self, tokens):
        # VAR = VALUE form
        #print "ASSIGNMENT %s %s" % (tokens[0], tokens[2])
        key = tokens[0]
        val = tokens[2]
        self.cnf.set(key, val)
        return self

    def HandleIncAssignment(self, tokens):
        # VAR += VALUE form
        #print "+= ASSIGNMENT %s %s" % (tokens[0], tokens[2])
        key = tokens[0]
        val = tokens[2]
        oldval = self.cnf.get(key)
        if oldval is not None:
            if (type(oldval) == type([])) or (type(val) == type([])):
                try:
                    newval = list(oldval) + list(val)
                except:
                    newval = textrepr(oldval) + textrepr(val)
            elif (type(oldval) == type(1)) or (type(val) == type(1)):
                try:
                    newval = int(oldval) + int(val)
                except:
                    newval = textrepr(oldval) + textrepr(val)
            else:
                newval = textrepr(oldval) + textrepr(val)
        else:
            newval = val
        self.cnf.set(key, newval)
        return self

    def Load(self):
        """
        Load the configuration file.
        Return a sflib.fileconf.config.Config instance.
        """
        import os, sys

        self.cnf = self.cnf or Config(initial = {'ENV': os.environ,
                                                 'sys': {'executable': sys.executable,
                                                         'path': sys.path,
                                                         'platform': sys.platform,
                                                         'version': sys.version,
                                                         'subversion': sys.subversion,
                                                         'version_info': sys.version_info,},
                                                 'os': {'sep': os.path.sep,
                                                        'pathsep': os.path.pathsep,
                                                        'pardir': os.path.pardir,
                                                        'curdir': os.path.curdir,},
                                                 })
        self.fh  = open(self.pathname, 'r')

        self.tparser = TokenParser(self.fh, pathname = self.pathname, context = self.cnf)

        while True:
            tokens = self.tparser.Tokenize()
            #print "tokens:%s" % tokens
            if tokens is None:
                break                   # EOF
            if len(tokens) == 0:
                continue

            if (len(tokens) == 1) and (type(tokens[0]) == type("")):
                # DIRECTIVE form
                self.HandleGenericSyntax(tokens)
            elif (len(tokens) == 2) and (tokens[0] == "include"):
                # INCLUDE form
                self.HandleInclude(tokens)
            elif (len(tokens) > 1) and (tokens[1] == '='):
                # VAR = VALUE form
                self.HandleAssignment(tokens)
            elif (len(tokens) > 1) and (tokens[1] == '+='):
                # VAR += VALUE form
                self.HandleIncAssignment(tokens)
            else:
                self.HandleGenericSyntax(tokens)
        self.fh.close()

        return self.cnf

def _test():
    """
    Test entry point
    """
    import doctest
    doctest.testmod()

def main():
    cp = ConfigParser("testconf.conf")
    cnf = cp.Load()
    print cnf

if __name__ == '__main__':
    #_test()
    main()
