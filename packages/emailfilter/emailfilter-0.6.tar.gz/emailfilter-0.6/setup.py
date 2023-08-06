#!/usr/bin/python -u
"""
Setup script for EMailFilter
Copyright (C) 2008 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information
"""

__progname__ = "emailfilter"
__version__ = (0, 6)
__dev_status__ = "Alpha"
__description__ = "A customizable e-mail content filter."
__start_line__ = "EMailFilter is a customizable e-mail content filter"
__end_line__ = "Copyright and License"
__license__ = "GNU GPL"
__author__ = "Peter A. Donis"
__author_email__ = "peterdonis@alum.mit.edu"
__rootfiles__ = ["CHANGES", "LICENSE", "TODO"]
__install_requires__ = ['plib']
__post_install__ = list("%s-setup-%s.py" % (__progname__, s) for s in ("paths", "modules"))

__classifiers__ = """
Environment :: Console
Intended Audience :: Developers
Intended Audience :: End Users/Desktop
Operating System :: MacOS :: MacOS X
Operating System :: POSIX
Operating System :: POSIX :: Linux
Programming Language :: Python
Topic :: Communications :: Email :: Filters
"""

if __name__ == '__main__':
    from SetupHelper import setup_main
    setup_main(globals())
