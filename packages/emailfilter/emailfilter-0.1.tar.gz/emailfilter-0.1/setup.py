#!/usr/bin/python -u
"""
Setup script for EMailFilter
Copyright (C) 2008 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information
"""

import sys
import os
from distutils.core import setup, Extension

# patch distutils if it can't cope with the "classifiers" or
# "download_url" keywords
if sys.version < '2.2.3':
    from distutils.dist import DistributionMetadata
    DistributionMetadata.classifiers = None
    DistributionMetadata.download_url = None

__version__ = "0.1"

# crib our long description from the opening paragraph of
# the README file
readme = open("README", 'rU')
lines = []
lastline = ""
started = False
try:
    for line in readme:
        line = line.strip()
        if started:
            if line == "Copyright and License":
                break
            else:
                lines.append(lastline)
        else:
            if line == "The EMailFilter Program":
                started = True
        lastline = line
finally:
    readme.close()
    del readme, started, line

__long_description__ = os.linesep.join(lines)
del lines

setup(
    name = "emailfilter",
    version = __version__,
    description = "A customizable e-mail content filter.",
    long_description = __long_description__,
    download_url = "http://www.peterdonis.net/computers/emailfilter-%s.tar.gz" % __version__,
    author = "Peter A. Donis",
    author_email = "peterdonis@alum.mit.edu",
    url = "http://www.peterdonis.net",
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Operating System :: POSIX',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Topic :: Communications :: Email :: Filters' ],
    # The extra jugglery with not "." in dirname and filename.startswith(".") is to mask out
    # hidden files and directories -- without this running setup from an svn working copy
    # goes haywire because it thinks that all the svn hidden files are scripts or data files
    scripts = ["%s/%s" % (dirname, filename)
        for dirname, _, files in os.walk('scripts') if not "." in dirname
        for filename in files if not filename.startswith(".")],
    data_files = [("lib/%s" % dirname, ["%s/%s" % (dirname, filename)
        for filename in files if not filename.startswith(".")])
        for dirname, _, files in os.walk('emailfilter') if files and not "." in dirname] )
