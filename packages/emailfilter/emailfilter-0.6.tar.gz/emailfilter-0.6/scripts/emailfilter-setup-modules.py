#!/usr/bin/env python
"""
SETUP-MODULES script for EMailFilter
Copyright (C) 2008-2009 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This script byte-compiles the emailfilter Python modules.
"""

import os
import compileall

binpath = os.path.dirname(__file__)
libpath = os.path.join(os.path.dirname(binpath), 'lib', 'emailfilter')

print "Byte-compiling emailfilter modules..."
compileall.compile_dir(libpath)

print "Done!"
