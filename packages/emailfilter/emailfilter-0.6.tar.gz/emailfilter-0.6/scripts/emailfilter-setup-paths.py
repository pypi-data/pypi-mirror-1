#!/usr/bin/env python
"""
EMAILFILTER-SETUP-PATHS.PY

EMailFilter Path Name Setup Script
Copyright (C) 2008-2009 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This script sets up the correct path names and other
variables in the emailfilter scripts.
"""

import sys
import os

binpath = os.path.dirname(__file__)
prefix = os.path.dirname(binpath)
libpath = os.path.join(prefix, 'lib', 'emailfilter')

if libpath not in sys.path:
    sys.path.append(libpath) # so import will see this path

defs = __import__('emailfilterdefs')

subst_dict = {'PREFIX': prefix}
# Hack to extract variables from the emailfilterdefs module; this
# ensures that everthing is using the same values
subst_dict.update((attrname, getattr(defs, attrname)) for attrname in
    ('EMAILFILTER_%s' % item for item in ('BUFSIZE', 'HOSTNAME', 'PORT')))
del prefix, defs
# Extra hack to allow different formatting of port number when installing
# as root, also encloses other variable values in quotes for safety
for key in subst_dict:
    if (os.getuid() == 0) and (key == 'EMAILFILTER_PORT'):
        subst_dict[key] = '$((%s + $UID))' % subst_dict[key]
    else:
        subst_dict[key] = '"%s"' % subst_dict[key]

def patch_file(filename):
    pathname = os.path.join(binpath, filename)
    f = open(pathname, 'r')
    try:
        s = f.read()
    finally:
        f.close()
    for varname, value in subst_dict.iteritems():
        oldstr = '%s=""' % varname
        newstr = '%s=%s' % (varname, value)
        if oldstr in s:
            print "Setting", varname, "to", value
            s = s.replace(oldstr, newstr)
    f = open(pathname, 'w')
    try:
        f.write(s)
    finally:
        f.close()

def do_setup():
    for filename in ("emailfilterc", "emailfilterd"):
        print "Patching", filename, "..."
        patch_file(filename)
    print "Done!"

if __name__ == '__main__':
    do_setup()
