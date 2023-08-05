#!/usr/bin/env python
"""
Module COMMON -- Python Base GUI Objects
Sub-Package GUI of Package PLIB -- Python GUI Framework
Copyright (C) 2008 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains common global objects for
the GUI sub-package. These are provided in a separate
module so that, if desired, these objects can be
mutated prior to instantiating your GUI application
(that is, prior to calling gui.runapp() to create
your application, or instantiating your own GUI
application class manually). These objects should
not be mutated after your application is running
because they are used on initialization to create
menu items, toolbar buttons, and actions.
"""

import sys
import os.path

from plib import stdlib
from plib.gui.defs import *

# list of 'automagically connected' signals (meaning that to catch
# them you have to override a method instead of calling setup_notify
# to have the signal sent to you)
automagic_signals = [SIGNAL_QUERYCLOSE, SIGNAL_BEFOREQUIT]

# useful combinations of action constants
ACTIONS_FILE = [ACTION_FILENEW, ACTION_FILEOPEN, ACTION_FILESAVE, ACTION_FILESAVEAS, ACTION_FILECLOSE]
ACTIONS_FILEMENU = ACTIONS_FILE + [ACTION_EXIT]
ACTIONS_ACTION = [ACTION_EDIT, ACTION_REFRESH, ACTION_ADD, ACTION_REMOVE, ACTION_OK, ACTION_CANCEL]
ACTIONS_OPTIONS = [ACTION_PREFS]
ACTIONS_OTHER = [ACTION_PREFS, ACTION_ABOUT, ACTION_EXIT]
ACTIONS_HELP = [ACTION_ABOUT]

# action dictionary
actiondict = { ACTION_FILENEW: ["filenew", "&New"],
    ACTION_FILEOPEN: ["fileopen", "&Open"],
    ACTION_FILESAVE: ["filesave", "&Save"],
    ACTION_FILESAVEAS: ["filesaveas", "Save &As"],
    ACTION_FILECLOSE: ["fileclose", "&Close"],
    ACTION_EDIT: ["button_edit", "&Edit"],
    ACTION_REFRESH: ["button_refresh", "&Refresh"],
    ACTION_ADD: ["button_add", "A&dd"],
    ACTION_REMOVE: ["button_remove", "Remo&ve"],
    ACTION_APPLY: ["apply", "Appl&y"],
    ACTION_COMMIT: ["button_ok", "Co&mmit"],
    ACTION_OK: ["button_ok", "&Ok"],
    ACTION_CANCEL: ["button_cancel", "Cance&l"],
    ACTION_PREFS: ["prefs", "&Preferences..."],
    ACTION_ABOUT: ["about", "A&bout..."],
    ACTION_EXIT: ["exit", "E&xit"] }

# action key list (needed to ensure proper ordering of actions,
# since the dictionary keys won't necessarily be ordered)
# TODO: make this dynamically update if actiondict is changed on the fly
actionkeylist = sorted(actiondict.keys())

# menu key dict (needed to properly sort and arrange menus)
menukeydict = { "&File": ACTIONS_FILEMENU,
    "Ac&tion": ACTIONS_ACTION,
    "&Options": ACTIONS_OPTIONS,
    "&Help": ACTIONS_HELP }

def keymenu(key):
    for item in menukeydict:
        if key in menukeydict[item]:
            return item
    return None

# button key group list (for use in adding separators)
buttonkeygroups = [ACTIONS_FILE, ACTIONS_ACTION, ACTIONS_OTHER]

# utility functions to work with key "groups"

def keygroup(key):
    for group in buttonkeygroups:
        if key in group:
            return group
    return None

def switchedgroup(lastkey, key):
    return (lastkey != 0) and (keygroup(lastkey) != keygroup(key))

# utility functions to get fully qualified pixmap path name

_pxdir = os.path.realpath(os.path.join(stdlib.plibpath, "gui", "_images"))

def pxname(aname, asuffix=None):
    if asuffix:
        return "%s-%s.png" % (aname, asuffix)
    return aname

# Return the fully qualified path name for a px file in the plib directory

def pxfile(aname):
    for asuffix in (sys.platform, os.name):
        result = os.path.join(_pxdir, pxname(aname, asuffix))
        if os.path.isfile(result):
            return result
    return pxname(aname)
