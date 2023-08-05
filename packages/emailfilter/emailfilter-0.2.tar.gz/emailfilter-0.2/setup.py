#!/usr/bin/python -u
"""
Generic setup script
*** Do not edit; fill in the desired variable values in setup_vars ***
Copyright (C) 2008 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This generic setup script automates much of the boilerplate; it
assumes that setup_vars.py exists in the same directory and
contains the following variables:

__progname__           -- name of the program
__version__            -- program version
__short_description__  -- one-line description
__long_description__   -- triple-quoted string containing long
                          description (may be read from README
                          instead, if so use next two variables
                          and omit this one)
__start_line__         -- contents of the line in README where the
                          long description should start
__end_line__           -- contents of the line in README where the
                          long description should end
__url_base__           -- base URL for download; assumes that the
                          full download URL is of the form
                          <base>/<progname>-<version>.<ext>
__url_type__           -- type of file being downloaded; can be
                          ('tar.gz', 'zip', 'exe', 'dmg') or
                          ('unix', 'windows', 'macosx')
__author__             -- author name
__author_email__       -- author e-mail address
__url__                -- home URL for the author or program
__classifiers__        -- triple-quoted string containing Trove
                          classifiers, one per line
__package_root__       -- subdir of the setup.py directory which is
                          the single 'root' for all packages; if
                          this is omitted any subdir which contains
                          an __init__.py file is treated as a package
__ext_names__          -- list of path names to extension modules
                          (starting from the setup.py directory); the
                          source code for each module is assumed to
                          be in the 'src' subdirectory of the module
                          directory (all C sources in that directory)
__script_root__        -- subdir of the setup.py directory which is
                          the 'root' containing all scripts; if this
                          is omitted it will be assumed to be 'scripts'
__data_dirs__          -- list of subdirs of the setup.py directory
                          which contain data files (other than package
                          data files); if this is omitted these
                          subdirs will be checked: <progname> (if
                          it's not a package), 'examples'; data dirs
                          are installed to 'share/<progname>/<datadir>'
                          except for <progname> if it's a data dir,
                          it goes to 'lib/<progname>'.
"""

import sys
import os
from distutils.core import setup, Extension

import setup_vars

# Hack to get around the fact that from <module> import *
# doesn't find variables that start with an underscore
vars = dir(setup_vars)
thismod = sys.modules[__name__]
for varname in vars:
    # Don't change the Python-provided vars
    if varname not in ('__builtins__', '__doc__', '__file__', '__name__'):
        setattr(thismod, varname, getattr(setup_vars, varname))
del setup_vars, thismod, varname

# patch distutils if it can't cope with the "classifiers" or
# "download_url" keywords
if sys.version < '2.2.3':
    from distutils.dist import DistributionMetadata
    DistributionMetadata.classifiers = None
    DistributionMetadata.download_url = None

# crib our long description from the opening section of
# the README file
if ('__start_line__' in vars) and ('__end_line__' in vars) and not ('__long_description__' in vars):
    readme = open("README", 'rU')
    lines = []
    lastline = ""
    started = False
    try:
        for line in readme:
            line = line.strip()
            if started:
                if line == __end_line__:
                    break
                else:
                    lines.append(lastline)
            else:
                if line == __start_line__:
                    started = True
            lastline = line
    finally:
        readme.close()
        del readme, started, line, lastline
    
    __long_description__ = '\n'.join(lines)
    del lines

# We'll store the lines that need to go into MANIFEST.in here (and add
# more below if applicable)
__manifest_in__ = []
for rootfile in ("install-all.sh", "setup_vars.py", "CHANGES", "LICENSE", "TODO"):
    if os.path.isfile(rootfile):
        __manifest_in__.append("include %s\n" % rootfile)
del rootfile

# Figure out the extension modules list (do this first so we can filter
# out extension directories from the package data list below)
__ext_modules__ = []
__ext_sourcedirs__ = []
if '__ext_names__' in vars:
    for extpath in __ext_names__:
        extdir, extname = os.path.split(extpath)
        srcdir = os.path.join(extdir, 'src')
        if os.path.isdir(srcdir):
            __ext_modules__.append(Extension(extpath, sources=[os.path.join(srcdir, filename)
                for filename in os.listdir(srcdir) if filename.endswith(".c")]))
            __ext_sourcedirs__.append(srcdir)
    del extpath, extdir, extname, srcdir, filename

# Figure out the package and package_data lists from the
# package root
__packages__ = []
__package_data__ = {}
if ('__package_root__' in vars):
    __package_dirs__ = [__package_root__]
else:
    __package_dirs__ = [entry for entry in os.listdir(".") if os.path.isdir(entry)
        and ("__init__.py" in os.listdir(entry))]
if __package_dirs__:
    for pkgdir in __package_dirs__:
        for directory, subdirs, files in os.walk(pkgdir):
            if "__init__.py" in files:
                __packages__.append(directory.replace('/', '.'))
            elif ("." not in directory) and (directory not in __ext_sourcedirs__):
                parentdir, thisdir = os.path.split(directory)
                if not parentdir in __package_data__:
                    __package_data__[parentdir] = []
                __package_data__[parentdir].append("%s/*.*" % thisdir)
                __manifest_in__.append("recursive-include %s *.*\n" % directory)
    del entry, pkgdir, directory, subdirs, files, parentdir, thisdir

# Figure out the scripts and data_files lists
# NOTE: The extra jugglery with not "." in dirname and filename.startswith(".") is to mask
# out hidden files and directories -- without this running setup from an svn working copy
# goes haywire because it thinks that all the svn hidden files are scripts or data files
__scripts__ = []
if '__script_root__' not in vars:
    __script_root__ = "scripts"
if os.path.isdir(__script_root__):
    __scripts__.extend("%s/%s" % (directory, filename)
        for directory, subdirs, files in os.walk("scripts") if not "." in directory
        for filename in files if not filename.startswith("."))
__data_files__ = []
if '__data_dirs__' not in vars:
    __data_dirs__ = ["examples"]
    if (__progname__ not in __package_dirs__):
        __data_dirs__.append(__progname__)
for datadir in __data_dirs__:
    if os.path.isdir(datadir):
        if datadir == __progname__:
            pathprefix = "lib"
        else:
            pathprefix = "share/%s" % __progname__
        __data_files__.extend(("%s/%s" % (pathprefix, directory), ["%s/%s" % (directory, filename)
            for filename in files if not filename.startswith(".")])
            for directory, subdirs, files in os.walk(datadir) if files and not "." in directory)
        __manifest_in__.append("recursive-include %s *.*\n" % datadir)
del datadir, pathprefix

# Write MANIFEST.in -- tmp file first so we don't clobber the current
# one if there's a problem
manifest_in = open("MANIFEST.in.tmp", 'w')
try:
    manifest_in.writelines(__manifest_in__)
finally:
    manifest_in.close()
if os.path.isfile("MANIFEST.in"):
    os.rename("MANIFEST.in", "MANIFEST.in.old")
os.rename("MANIFEST.in.tmp", "MANIFEST.in")
if os.path.isfile("MANIFEST.in.old"):
    os.remove("MANIFEST.in.old")
del manifest_in

del sys, os, vars

urltypes = {'unix': "tar.gz", 'windows': "zip", 'macosx': "dmg"}
try:
    __url_ext__ = urltypes[__url_type__]
except KeyError:
    __url_ext__ = __url_type__
del urltypes

if __name__ == '__main__':
    setup(
        name = __progname__,
        version = __version__,
        description = __short_description__,
        long_description = __long_description__,
        download_url = "%s/%s-%s.%s" % (__url_base__, __progname__, __version__, __url_ext__),
        author = __author__,
        author_email = __author_email__,
        url = __url__,
        classifiers = __classifiers__.strip().splitlines(),
        packages = __packages__,
        package_data = __package_data__,
        ext_modules = __ext_modules__,
        scripts = __scripts__,
        data_files = __data_files__
        )
