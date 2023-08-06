#!/usr/bin/env python
"""
PLIB-SETUP-PATHS.PY
Post-install script to determine standard pathnames
Copyright (C) 2008 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This script determines the absolute pathnames for the
following key locations:

-- The main python directory;
-- The site-packages directory;
-- The PLIB package root directory;
-- The default directory for third-party binaries;
-- The default directory for third-party shared files.

This script only needs to be run on installation of PLIB
or if the python installation directories are changed.
"""

import sys
import os

if os.name == 'posix':
    binpath = os.path.dirname(__file__)

elif os.name == 'nt':
    pythondir = "C:\\Python" + sys.version[:3]
    pythondir = pythondir.replace('.', '')
    binpath = os.path.join("C:\\" + pythondir, "Scripts")

else:
    binpath = ''

if binpath:
    sharepath = os.path.join(os.path.dirname(binpath), 'share')

else:
    sharepath = ''

if sys.platform == 'win32':
    pythonpath = os.path.join(sys.prefix, 'Lib')
else:
    pythonpath = os.path.join(sys.prefix, 'lib', "python" + sys.version[:3])
    if not os.path.exists(pythonpath):
        pythonpath = pythonpath[:-3]
if not os.path.exists(pythonpath):
    raise OSError, "python directory not found!"

if sys.platform == 'darwin':
    # Utility function for later
    if pythonpath.endswith(sys.version[:3]):
        def joinpath(*args):
            return os.path.join(os.path.dirname(binpath), 'lib', 'python' + sys.version[:3], *args)
    else:
        def joinpath(*args):
            return os.path.join(os.path.dirname(binpath), 'lib', 'python', *args)

sitepath = os.path.join(pythonpath, 'site-packages')
if (not os.path.exists(sitepath)) and (sys.platform == 'darwin'):
    # Hack to guess alternate site path locations for OS X
    sitepath = '/Library/Python/%s/site-packages' % sys.version[:3]
    if (not os.path.exists(sitepath)) and (os.path.dirname(binpath) != sys.prefix):
        sitepath = joinpath('site-packages')
if not os.path.exists(sitepath):
    raise OSError, "site-packages directory not found!"

plibpath = os.path.join(sitepath, "plib")
if not os.path.exists(plibpath):
    plibpath = ''
    for p in sys.path:
        p = os.path.join(p, "plib")
        if os.path.exists(p):
            plibpath = p
            break
    if (not plibpath) and (sys.platform == 'darwin'):
        # On Mac OS X it's possible that we installed PLIB into a
        # directory that isn't on sys.path (for example, we might have
        # installed into /usr/local but Python is in a framework); if
        # so, we need to symlink plibpath into site-packages
        if (os.path.dirname(binpath) != sys.prefix):
            plibpath = joinpath('site-packages', 'plib')
            if os.path.exists(plibpath):
                print "Creating symlink of PLIB directory into site-packages..."
                os.symlink(plibpath, os.path.join(sitepath, 'plib'))
            else:
                plibpath = ''
    if not plibpath:
        raise OSError, "plib directory not found!"

print "Writing _paths.py module to stdlib directory..."

module_vars = ['pythonpath', 'sitepath', 'plibpath', 'binpath', 'sharepath']
outpath = os.path.join(plibpath, "stdlib")
outfilename = "_paths.py"
descr = "STDLIB Pathname"

try:
    from plib import setuputils
except ImportError:
    # We're on Mac OS X and installed PLIB into a directory that isn't on
    # sys.path, so we monkey patch it in
    sys.path.insert(0, plibpath)
    import setuputils

setuputils.write_setup_file(__name__, module_vars, outpath, outfilename, descr)

print "PLIB pathname setup done!"
