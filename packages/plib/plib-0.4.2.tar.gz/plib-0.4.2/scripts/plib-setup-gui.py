#!/usr/bin/env python
"""
SETUP-GUI script for Package PLIB
Copyright (C) 2008 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This script determines what GUI toolkits are present on the system,
and writes a _setup.py module to the plib.gui directory that defines
appropriate constants. This module is then loaded by the main gui module
to determine which toolkits are available for use. The script should be
run after the sub-packages for PLIB are installed, since it uses some of
them.

Note that this script should only need to be run on initial installation
of PLIB or when toolkit packages are installed or uninstalled.
"""

import os
import compiler

from plib.stdlib import plibpath

# Check which GUI toolkits are available

qt_present = False
try:
    import qt
    qt_present = True
except ImportError:
    pass

kde_present = False
try:
    import kdecore
    kde_present = True
except ImportError:
    pass

gtk_present = False
try:
    import pygtk
    pygtk.require('2.0')
    import gtk
    gtk_present = True
except ImportError:
    pass
except AssertionError:
    pass

wx_present = False
try:
    import wx
    wx_present = True
except ImportError:
    pass

qt4_present = False
try:
    from PyQt4 import Qt
    qt4_present = True
except ImportError:
    pass

bool_disp = {False: "not present", True: "present"}

print "Qt:", bool_disp[qt_present]
print "KDE:", bool_disp[kde_present]
print "Gtk:", bool_disp[gtk_present]
print "WxWidgets:", bool_disp[wx_present]
print "Qt 4:", bool_disp[qt4_present]

print "Writing _setup.py module to GUI directory..."

module_vars = [
    ("QT_PRESENT", qt_present),
    ("KDE_PRESENT", kde_present),
    ("GTK_PRESENT", gtk_present),
    ("WX_PRESENT", wx_present),
    ("QT4_PRESENT", qt4_present) ]

lines = [
    "#!/usr/bin/env python\n",
    "# _SETUP.PY -- PLIB.GUI Toolkit Setup Module\n",
    "# *** This module is automatically generated; do not edit. ***\n",
    "\n" ]

lines.extend(("%s = %s\n" % vars for vars in module_vars))

outpath = os.path.join(plibpath, "gui", "_setup.py")
outfile = open(outpath, 'w')
outfile.writelines(lines)
outfile.close()

print "Byte-compiling _setup.py..."
compiler.compileFile(outpath)

print "PLIB GUI setup done!"
