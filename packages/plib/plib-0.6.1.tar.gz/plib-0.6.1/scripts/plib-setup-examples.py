#!/usr/bin/env python
"""
SETUP-EXAMPLES script for Package PLIB
Copyright (C) 2008-2009 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This script sets up symlinks in $PREFIX/bin to each of the
example programs that come with PLIB, and byte-compiles
the examples, on systems that support symlinks (i.e.,
POSIX systems only). On other systems (i.e., Windows),
the example programs and their associated files are instead
simply copied to the Python/Scripts directory.
"""

import sys
import os
import glob

from plib.stdlib import binpath, sharepath

print "Setting up example programs..."

if os.name == 'posix':
    import compileall
    
    def pre_output(binpath, examplepath):
        print "Creating symlinks in", binpath, "to examples in", examplepath, "..."
    
    def post_output():
        print "Byte-compiling examples..."
        compileall.compile_dir(examplepath)
    
    glob_pattern = '*.py'
    process_fn = os.symlink

elif os.name == 'nt':
    import shutil
    
    def pre_output(binpath, examplepath):
        print "Copying examples from", examplepath, "to", binpath, "..."
    
    def post_output():
        pass
    
    glob_pattern = '*.*'
    process_fn = shutil.copyfile

if binpath:
    examplepath = os.path.join(sharepath, 'plib', 'examples')
    
    pre_output(binpath, examplepath)
    
    pyfiles = [filename for dirname in glob.glob(os.path.join(examplepath, '*'))
        for filename in glob.glob('%s/%s' % (dirname, glob_pattern))]
    
    for pyfile in pyfiles:
        destfile = os.path.join(binpath, os.path.basename(pyfile))
        if os.path.exists(destfile):
            os.remove(destfile)
        process_fn(pyfile, destfile)
    
    post_output()
    
    print "PLIB examples setup done!"
