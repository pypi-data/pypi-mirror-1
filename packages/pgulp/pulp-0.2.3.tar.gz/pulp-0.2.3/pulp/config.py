#!/usr/bin/env python2.4
#
# (c) 2007 Andreas Kostyrka
#

"""manage a .pulprc configfile"""

import ConfigParser as cp
import os, sys

class Config(cp.ConfigParser):
    def __init__(self):
        filename = os.path.expanduser("~/.pulprc")
        cp.ConfigParser.__init__(self)
        self.read(filename)

    def save(self):
        self.write(file(os.path.expanduser("~/.pulprc"), "w"))

    def usage(self, msg=None):
        def w(string):
            sys.stderr.write(string + "\n")
        w("usage: %s arguments" % sys.argv[0])
        w("arguments like section.name show the current value.")
        w("arguments like section.name=value change the current value.")
        w("Interesting configuration parameters include pulp.username and pulp.password")
        if msg:
            w(">>> " + msg)
        sys.exit(3)
        
    def __call__(self):
        args = sys.argv[1:]
        if len(args) == 0:
            self.usage()
        dirty = False
        for a in args:
            if "=" in a:
                name, value = a.split("=", 1)
            else:
                name, value = a, None
            if name.count(".") != 1:
                self.usage("%s is not a valid name" % name)
            section, name = name.split(".", 1)
            if value is None:
                try:
                    sys.stdout.write("%s.%s=%s\n" % (section, name, self.get(section, name)))
                except (cp.NoSectionError, cp.NoOptionError):
                    self.usage("%s.%s is not a valid name" % (section, name))
            else:
                if not self.has_section("pulp"):
                    self.add_section("pulp")
                try:
                    self.set(section, name, value)
                except cp.NoSectionError:
                    self.usage("%s.%s is not a valid name" % (section, name))

                dirty = True
        if dirty:
            self.save()
    def get(self, section, option, raw=False, vars=None, default=cp.ConfigParser):
        try:
            return cp.ConfigParser.get(self, section, option, raw=raw, vars=vars)
        except (cp.NoSectionError, cp.NoOptionError):
            if default is cp.ConfigParser:
                raise
            else:
                return default

        
main = Config()                   # make it callable from the cmdline!

        
        

