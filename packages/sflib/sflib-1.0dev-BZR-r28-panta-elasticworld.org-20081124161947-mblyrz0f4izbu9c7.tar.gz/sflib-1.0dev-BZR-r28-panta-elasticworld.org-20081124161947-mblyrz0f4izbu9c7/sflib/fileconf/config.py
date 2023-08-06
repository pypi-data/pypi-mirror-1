#!/usr/bin/env python
# ex:ts=8:sw=4:sts=4:et
# -*- tab-width: 8; c-basic-offset: 4; indent-tabs-mode: t -*-
#
# Copyright (C) 2008 Marco Pantaleoni. All rights reserved

"""
   >>> o = Config()
   >>> o.port = 80
   >>> o.url  = "http://www.test.com"

   >>> print o.port
   80

   >>> print o.url
   http://www.test.com

   >>> print o
     port = 80,
     url = 'http://www.test.com',
   <BLANKLINE>

   >>> o.get("port.type")

   >>> o.set("port.type", "TCP")
   'TCP'

   >>> o.get("port.type")
   'TCP'

   >>> print o
     port = 80 {{
       type = 'TCP',
     }},
     url = 'http://www.test.com',
   <BLANKLINE>
"""

class ConfigKey(object):
    def __init__(self, name, value, config):
        self.name    = name
        self.value   = value
        self.config  = config

    def __repr__(self):
        return "<%s, %s>" % (self.value, self.config)

class Config(object):
    def __init__(self, parent=None, initial={}):
        self.parent = parent
        self.values = {}

        self.init_from_dict(initial)

    def init_from_dict(self, init_dict):
        for k, v in init_dict.items():
            if isinstance(v, dict) or (type(v) == type({})) or (hasattr(v, 'items') and hasattr(v, '__getitem__')):
                cnf = Config(parent = self, initial = v)
                c_key = ConfigKey(k, None, cnf)
                self.values[k] = c_key
            else:
                self.set(k, v)
        return self

    def __getattr__(self, name):
        if name == 'values':
            return self.values
        if name == 'parent':
            return self.parent
        if name in self.values:
            c_key = self.values[name]
            return c_key.value
        else:
            return None
        raise AttributeError, name

    def __setattr__(self, name, value):
        if name in ('values', 'parent'):
            super(Config, self).__setattr__(name, value)
        else:
            self._set_value(name, value)

    def __delattr__(self, name):
        if name in self.values:
            del self.values[name]

    def empty(self):
        return len(self.values.keys()) == 0

    def get(self, name, default=None):
        """
        Get a config value using a key 'name' having a hierarchical form,
        like:

          remote.server.name
        """
        name_components = name.split('.')
        return self._get_components(name_components, default)

    def set(self, name, value):
        """
        Perform a value assignment with a key 'name' having a hierarchical form,
        like:

          remote.server.name
        """
        name_components = name.split('.')
        return self._set_components(name_components, value)

    def _get_components(self, name_components, default=None):
        first_comp = name_components[0]
        if len(name_components) == 1:
            return self._get_value(first_comp, default)
        if first_comp in self.values:
            c_key = self.values[first_comp]
            cnf   = c_key.config
            return cnf._get_components(name_components[1:], default)
        return default

    def _set_components(self, name_components, value):
        """Helper function for hierarchical assignment."""
        #print "_assign_components(%s, %s)" % (repr(name_components), repr(value))
        first_comp = name_components[0]
        if len(name_components) == 1:
            self._set_value(first_comp, value)
            return value
        if first_comp in self.values:
            c_key = self.values[first_comp]
            cnf   = c_key.config
            return cnf._set_components(name_components[1:], value)

        assert first_comp not in self.values

        self._set_value(first_comp, None)
        c_key = self.values[first_comp]
        cnf   = c_key.config
        return cnf._set_components(name_components[1:], value)

    def _get_value(self, name, default=None):
        """
        Get the value for a non-hierarchical key 'name'.
        """
        if name in self.values:
            c_key = self.values[name]
            return c_key.value
        return default

    def _set_value(self, name, value):
        """
        Set the value for a non-hierarchical key 'name'.
        """
        if isinstance(value, ConfigKey):
            self.values[name] = value
        else:
            if name in self.values:
                c_key = self.values[name]
                assert isinstance(c_key, ConfigKey)
                c_key.value = value
            else:
                cnf = Config(parent = self)
                c_key = ConfigKey(name, value, cnf)
            self.values[name] = c_key
        return self

    def __repr__(self):
        return Config.pprint(self)
##        r = "{"
##        keys = self.values.keys()
##        keys.sort()
##        for k in keys:
##            c_key = self.values[k]
##            if c_key.config.empty():
##                v_repr = "%s" % c_key.value
##            else:
##                v_repr = "%s %s" % (c_key.value, c_key.config)
##            r += "%s: %s,\n" % (k, v_repr)
##        r += "}"
##        return r

    def pprint(cls, cnf, indent = 2, done = {}):
        import string
        done = done or {}

        if isinstance(cnf, Config):
            sb = []

            keys = cnf.values.keys()
            keys.sort()
            for k in keys:
                c_key = cnf.values[k]

                value  = c_key.value
                subcnf = c_key.config

                sb.append(" " * indent)

                if (type(value) == type({})) and (not done[value]):
                    done[value] = True
                    sb.append("%s = {\n" % k)
                    sb.append(Config.pprint(value, indent + 2, done))
                    if subcnf and (not subcnf.empty()):
                        done[subcnf] = True
                        sb.append(" {{\n")
                        sb.append(Config.pprint(subcnf, indent + 2, done))
                        sb.append(" " * indent + "}}")
                    sb.append(" " * indent + "},\n")
                else:
                    sb.append("%s = %s" % (k, repr(value)))
                    if subcnf and (not subcnf.empty()):
                        done[subcnf] = True
                        sb.append(" {{\n")
                        sb.append(Config.pprint(subcnf, indent + 2, done))
                        sb.append(" " * indent + "}}")
                    sb.append(",\n")
            return string.join(sb, "")
        elif type(cnf) == type({}):
            sb = []

            keys = cnf.keys()
            keys.sort()
            for k in keys:
                value  = cnf[k]

                sb.append(" " * indent)

                if (type(value) == type({})) and (not done[value]):
                    done[value] = True
                    sb.append("%s = {\n" % k)
                    sb.append(Config.pprint(value, indent + 2, done))
                    sb.append(" " * indent + "},\n")
                else:
                    sb.append("%s = %s" % (k, repr(value)))
                    sb.append(",\n")
            return string.join(sb, "")
        else:
            return "%s\n" % cnf
        return "%s\n" % cnf
    pprint = classmethod(pprint)

def _test():
    """
    Test entry point
    """
    import doctest
    doctest.testmod()

if __name__ == '__main__':
    _test()
