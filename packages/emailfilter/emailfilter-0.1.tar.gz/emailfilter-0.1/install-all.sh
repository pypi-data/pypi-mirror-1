#!/bin/sh
# Installation script for EMailFilter
# Copyright (C) 2008 by Peter A. Donis
#
# Released under the GNU General Public License, Version 2
# See the LICENSE and README files for more information
#
# This script runs the setup.py install script for EMailFilter
# and then runs the post-install scripts

python setup.py install $@
echo Running post-install scripts...
emailfilter-setup-modules.py
emailfilter-setup-paths.py
