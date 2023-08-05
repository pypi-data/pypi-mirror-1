#!/usr/bin/env python
"""
Internal Module _GUI
Sub-Package GUI of Package PLIB -- Python GUI Framework
Copyright (C) 2008 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the code to determine what GUI toolkit
should be used. It is for internal use by the other GUI
modules; user applications should not need to import it
since the GUI sub-package itself contains the gui_toolkit
variable in its namespace.
"""

import sys
import os

from plib.gui.defs import *
from plib.gui._setup import *

# GUI toolkit determination -- this has to be here to avoid circular imports
# among the various GUI modules
gui_toolkit = 0

# If environment variable present and correct, it determines the toolkit
env_toolkit_name = os.getenv("GUI_TOOLKIT")
if env_toolkit_name is not None:
    # Hack to allow env var to be either numeric value or name of the constant
    try:
        gui_toolkit = int(env_toolkit_name)
    except ValueError:
        for name in dir(sys.modules[__name__]):
            if name == env_toolkit_name:
                gui_toolkit = getattr(sys.modules[__name__], name)
                break

# Clean up namespace
del env_toolkit_name

# If toolkit not set above, detect desktop environment
if gui_toolkit == 0:
    desktop_session = os.getenv('DESKTOP_SESSION')
    window_mgr = os.getenv('WINDOWMANAGER')
    
    # check KDE/Qt first
    if KDE_PRESENT or QT_PRESENT:
        kde_session = 'KDE_FULL_SESSION' in os.environ
        kde_desktop = (desktop_session == 'kde')
        kde_winmgr = isinstance(window_mgr, basestring) and (window_mgr.find('kde') > -1)
        # TODO: check if kdeinit (kde root process) and kwin (kde window mgr) are running
        
        # if KDE is running, default to KDE if PyKDE is present, otherwise Qt
        if kde_session or kde_desktop or kde_winmgr:
            if KDE_PRESENT:
                gui_toolkit = GUI_KDE
            else:
                gui_toolkit = GUI_QT
        
        # clean up namespace
        del kde_session, kde_desktop, kde_winmgr
    
    # check GTK if KDE/Qt didn't work
    if (gui_toolkit == 0) and GTK_PRESENT:
        gnome_session = 'GNOME_DESKTOP_SESSION_ID' in os.environ
        gnome_desktop = (desktop_session == 'gnome')
        gnome_winmgr = isinstance(window_mgr, basestring) and (window_mgr.find('gnome') > -1)
        # TODO: check if gconfd running and if /desktop/gnome/applications/browser key present
        
        # if Gnome is running, default to GTK (we could use wx instead of gtk here but
        # since wx with gtk present is just a wrapper around gtk we prefer to cut out
        # the middleman)
        if gnome_session or gnome_desktop or gnome_winmgr:
            gui_toolkit = GUI_GTK
        
        # clean up namespace
        del gnome_session, gnome_desktop, gnome_winmgr
    
    # default to wxWidgets if present
    if (gui_toolkit == 0) and WX_PRESENT:
        gui_toolkit = GUI_WX
    
    # clean up namespace
    del desktop_session, window_mgr
    
    # if no toolkit found, error
    if gui_toolkit == 0:
        sys.exit("No GUI toolkit found; cannot run GUI application.")
