#!/usr/bin/env python
"""
EMAILFILTERD.PY
Copyright (C) 2008-2009 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

Script to run EMAILFILTER.PY in daemon mode. This mode is
provided to avoid having to incur the overhead of loading
and parsing the Python code for EMAILFILTER.PY, and any
additional test function modules that it loads, for each
e-mail message scanned. Instead, this script runs in the
background as a daemon, so that all the loading and parsing
of the filtering code is done only once, when the daemon
starts. Actual e-mail scanning is then done by the client
script, EMAILFILTERC.PY, which connects to this one via a
socket; the net result is that stdin for EMAILFILTERC.PY
is piped to EMAILFILTER.PY through the socket, and the
result string from EMAILFILTER.PY is piped to stdout for
EMAILFILTERC.PY back through the socket. Thus, running
EMAILFILTERC.PY should give identical results on any
e-mail message to running EMAILFILTER.PY in standalone
mode, but without having to load and parse EMAILFILTER.PY
and its test function modules every time.
"""

from signal import SIGHUP

from plib.classes import PTCPServer
from plib.stdlib.io.blocking import BaseRequestHandler

import emailfilter
from emailfilterdefs import *

class EMailFilterHandler(BaseRequestHandler):
    """ Request Handler class for e-mail filter daemon; reads data from
    the request socket, calls EMAILFILTER.PY to process it, then writes
    the result data back to the socket. """
    
    bufsize = EMAILFILTER_BUFSIZE
    
    def process_data(self):
        try:
            result = emailfilter.main(self.read_data)
        except:
            result = self.read_data
        self.start(result)

class EMailFilterServer(PTCPServer):
    """ Server class for e-mail filter daemon. """
    
    server_name = EMAILFILTER_NAME
    bind_addr = EMAILFILTER_ADDR
    handler_class = EMailFilterHandler
    sig_methods = {SIGHUP: 'sighup_handler'}
    
    def sighup_handler(self, sig, frame):
        """
        Reap any zombies on HUP -- note that we do not return a
        sig value (meaning we return None), so that the server does
        not shut down.
        """
        
        self.log_msg("collecting finished child processes")
        self.collect_children()

def main():
    # Run the server -- it will auto-destruct when serve_forever returns
    EMailFilterServer().serve_forever()

if __name__ == '__main__':
    main()
