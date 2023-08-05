#!/usr/bin/env python
"""
SETUP-EXAMPLES script for Package PLIB
Copyright (C) 2008 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This script sets up symlinks in $PREFIX/bin to each of the
example programs that come with PLIB, and byte-compiles
the examples. Note that the symlinks are only set up if
the OS supports them (i.e., POSIX systems only).
"""

import sys
import os
import glob
import compileall

binpath = os.path.dirname(__file__)
sharepath = os.path.join(os.path.dirname(binpath), 'share', 'plib', 'examples')

if os.name == 'posix':
    pyfiles = [filename for dirname in glob.glob(os.path.join(sharepath, '*'))
        for filename in glob.glob('%s/*.py' % dirname)]
    print "Creating symlinks in", binpath, "to examples in", sharepath, "..."
    for pyfile in pyfiles:
        linkfile = os.path.join(binpath, os.path.basename(pyfile))
        if os.path.exists(linkfile):
            os.remove(linkfile)
        os.symlink(pyfile, linkfile)

print "Byte-compiling examples..."
compileall.compile_dir(sharepath)

print "PLIB examples setup done!"
