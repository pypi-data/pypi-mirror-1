#!/usr/bin/python -u
"""
Setup script for PLIB package
Copyright (C) 2008 by Peter A. Donis
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
readme = open("README")
lines = []
lastline = ""
started = False
try:
    for line in readme:
        line = line.strip()
        if started:
            if line == "The Zen of PLIB":
                break
            else:
                lines.append(lastline)
        else:
            if line == "The PLIB Package":
                started = True
        lastline = line
finally:
    readme.close()
    del readme, started, line

__long_description__ = os.linesep.join(lines)
del lines

module1 = Extension("plib/extensions/_extensions",
    sources = ["plib/extensions/src/_extensions.c"])

setup(
    name = "plib",
    version = __version__,
    description = "PLIB provides a top-level namespace for a number of useful sub-packages and modules.",
    long_description = __long_description__,
    download_url = "http://www.peterdonis.net/computers/plib-0.1.tar.gz",
    author = "Peter A. Donis",
    author_email = "peterdonis@alum.mit.edu",
    url = "http://www.peterdonis.net",
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Environment :: MacOS X',
        'Environment :: Win32 (MS Windows)',
        'Environment :: X11 Applications :: GTK',
        'Environment :: X11 Applications :: KDE',
        'Environment :: X11 Applications :: Qt',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules' ],
    packages = [
        'plib', 'plib.classes', 'plib.extensions',
        'plib.gui', 'plib.gui._base', 'plib.gui._toolkits', 'plib.gui._widgets',
        'plib.gui._toolkits._gtk', 'plib.gui._toolkits._kde', 'plib.gui._toolkits._qt', 'plib.gui._toolkits._wx',
        'plib.ini', 'plib.stdlib', 'plib.utils', 'plib.xml' ],
    package_data = {
        'plib': ["test/*.*"],
        'plib.gui': ["_images/*.*"] },
    ext_modules = [module1],
    scripts = ["scripts/%s" % filename for _, _, files in os.walk('scripts') for filename in files],
    data_files = [("share/plib/%s" % dirname, ["%s/%s" % (dirname, filename) for filename in files])
        for dirname, _, files in os.walk('examples') if files] )
