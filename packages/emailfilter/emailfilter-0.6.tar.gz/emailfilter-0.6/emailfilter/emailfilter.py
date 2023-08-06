#!/usr/bin/env python
"""
EMAILFILTER.PY
Copyright (C) 2008-2009 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

An e-mail spam filtering program intended to supplement (not replace!)
statistics-based filters with tailored content-based tweaks.

This script takes a single e-mail message in RFC 2822 format on stdin
and outputs the same message on stdout but with 'X-' type headers
added based on content filtering specified in user-defined Python
modules. This specification is done via the specs variable in this
script, which is a mapping of 'X-' type header names to filter
function objects. This script builds the specs mapping by looking
for Python files in its directory whose names begin with "filter_";
it expects that each such file will be an importable module with a
function in it having the same name as the module; that function will
be the one called by this script.

Each function (actually, any callable object with the right signature
will work) must take one argument, which is the e-mail message, and
must output either None (if it determines that no header is to be
added) or a string, which will be added as the value of the 'X-' type
header field named in the specs mapping.

If this script is run in stand-alone mode, the input string is read from
stdin and the result string is written to stdout. Note that this is *not*
the recommended mode of operation for actual e-mail scanning; it is intended
for testing only. For actual e-mail scanning, it is recommended to run in
daemon mode to avoid the overhead of loading and parsing Python code for
all of the testing functions for each e-mail message to be processed; see
EMAILFILTERD.PY for more information.
"""

import sys
import os
import glob
from email import Generator, message_from_string
from cStringIO import StringIO

def _flag_name(modname):
    """ Returns the 'X-' flag name to be mapped to the module named modname. """
    return os.path.basename(modname)[7:-3].replace('_', '-')

def _filter_func(modname):
    """ Returns the filter function object from the module named modname. """
    modname = os.path.basename(modname)[:-3]
    return getattr(__import__(modname), modname)

def _dir_func(dirname, fileglob):
    if dirname:
        return os.path.join(os.path.expanduser(dirname), fileglob)
    return fileglob

specs = {}
for dirname in ("", os.path.join("~", ".emailfilter")):
    sys.path.append(os.path.expanduser(dirname)) # hack to make __import__ see dirname
    specs.update(('X-%s' % _flag_name(modname), _filter_func(modname))
        for modname in glob.glob(_dir_func(dirname, "filter_*.py")))
del _flag_name, _filter_func, _dir_func

def process(msg):
    """ Run message through each test given in specs. """
    
    for spec, func in specs.iteritems():
        if func is not None:
            result = func(msg)
            if result is not None:
                msg[spec] = result

def main(inputstr):
    """ Take message stored in inputstr, process it, then return the result string. """
    
    msg = message_from_string(inputstr)
    process(msg)
    f = StringIO()
    g = Generator.Generator(f, mangle_from_=False)
    g.flatten(msg)
    return f.getvalue()

if __name__ == '__main__':
    # Run in standalone mode
    s = sys.stdin.read()
    r = main(s)
    sys.stdout.write(r)
