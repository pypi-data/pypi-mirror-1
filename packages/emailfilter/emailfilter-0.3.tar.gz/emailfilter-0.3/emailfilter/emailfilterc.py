#!/usr/bin/env python
"""
EMAILFILTERC.PY
Copyright (C) 2008 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

Client script to communicate with EMAILFILTERD.PY through a
TCP socket. See EMAILFILTERD.PY for more information on this
mode of operation for EMAILFILTER.PY. This script is intended
to be set up as a filter to be run by your e-mail client; each
time it is run it takes one e-mail message on stdin, pipes it
through EMAILFILTER.PY via the EMAILFILTERD.PY daemon, and
writes the result to stdout. The details of setting this script
up to run as an e-mail filter will depend on your e-mail client.
"""

import sys

from plib.classes import PTCPClient

from emailfilterdefs import *

class EMailFilterClient(PTCPClient, EMailFilterMixin):
    """ Client class for email filter; creates a socket and
    connects it to the EMAILFILTERD.PY daemon. Its methods
    can then be called to send and receive data. """
    
    server_name = EMAILFILTER_NAME
    server_addr = EMAILFILTER_ADDR
    
    def process_data(self, s):
        if self.sock_result == 0:
            self.send_data(s)
            return self.recv_data()
        
        # If socket connection failed, pipe input direct to output
        return s

def main():
    s = sys.stdin.read()
    r = EMailFilterClient().process_data(s) # client will auto-destruct
    sys.stdout.write(r)

if __name__ == '__main__':
    main()
