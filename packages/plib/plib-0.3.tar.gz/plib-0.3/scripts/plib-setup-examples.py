#!/usr/bin/env python
"""
SETUP-EXAMPLES script for Package PLIB
Copyright (C) 2008 by Peter A. Donis

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

if os.name == 'posix':
    import compileall
    
    def pre_output(binpath, sharepath):
        print "Creating symlinks in", binpath, "to examples in", sharepath, "..."
    
    def post_output():
        print "Byte-compiling examples..."
        compileall.compile_dir(sharepath)
    
    binpath = os.path.dirname(__file__)
    glob_pattern = '*.py'
    process_fn = os.symlink

elif os.name == 'nt':
    import shutil
    
    def pre_output(binpath, sharepath):
        print "Copying examples from", sharepath, "to", binpath
    
    def post_output():
        pass
    
    pythondir = "C:\\Python" + sys.version[:3] # TODO: sys.prefix?
    pythondir = pythondir.replace('.', '')
    
    binpath = os.path.join("C:\\" + pythondir, "Scripts")
    glob_pattern = '*.*'
    process_fn = shutil.copyfile

else:
    binpath = ''

if binpath:
    sharepath = os.path.join(os.path.dirname(binpath), 'share', 'plib', 'examples')
    
    pre_output(binpath, sharepath)
    
    pyfiles = [filename for dirname in glob.glob(os.path.join(sharepath, '*'))
        for filename in glob.glob('%s/%s' % (dirname, glob_pattern))]
    
    for pyfile in pyfiles:
        destfile = os.path.join(binpath, os.path.basename(pyfile))
        if os.path.exists(destfile):
            os.remove(destfile)
        process_fn(pyfile, destfile)
    
    post_output()
    
    print "PLIB examples setup done!"
