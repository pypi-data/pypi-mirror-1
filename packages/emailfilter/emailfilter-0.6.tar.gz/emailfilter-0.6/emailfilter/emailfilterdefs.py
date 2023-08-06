#!/usr/bin/env python
"""
EMAILFILTERDEFS.PY
Copyright (C) 2008-2009 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

Common definitions for emailfilter scripts.
"""

import os

EMAILFILTER_NAME = "emailfilter"
EMAILFILTER_BUFSIZE = 65536
EMAILFILTER_HOSTNAME = "localhost"
EMAILFILTER_PORT = 5590 + os.getuid()

EMAILFILTER_ADDR = (EMAILFILTER_HOSTNAME, EMAILFILTER_PORT)

#EMAILFILTER_QUEUESIZE = 5 # queue size defaults to 5 in SocketServer anyway
