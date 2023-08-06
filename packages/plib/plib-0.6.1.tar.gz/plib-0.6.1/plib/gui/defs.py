#!/usr/bin/env python
"""
Module DEFS -- Common GUI Definitions
Sub-Package GUI of Package PLIB -- Python GUI Framework
Copyright (C) 2008-2009 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

Defines common constants and functions used by various GUI modules.
"""

import sys

# general constants
default_font_size = 10

# constants for referring to GUI toolkits
GUI_QT = 1
GUI_GTK = 2
GUI_WX = 3
GUI_KDE = 4
GUI_QT4 = 5
GUI_KDE4 = 6

# message box types
MBOX_INFO = 0
MBOX_WARN = 1
MBOX_ERROR = 2
MBOX_QUERY = 3

# constants for message box responses
answerNone = 0
answerYes = 1
answerNo = 2
answerCancel = 3
answerOK = 4

# constants for alignment
ALIGN_LEFT = 1
ALIGN_CENTER = 2
ALIGN_RIGHT = 3
ALIGN_TOP = 4
ALIGN_BOTTOM = 5
ALIGN_JUST = 9

# Layout constants
LAYOUT_NONE = 0
LAYOUT_HORIZONTAL = 1
LAYOUT_VERTICAL = 2

# Panel style constants
PANEL_NONE = 0
PANEL_BOX = 1
PANEL_RAISED = 2
PANEL_SUNKEN = 3

# Prefs dialog section style constants
SECTION_TAB = 0 # this is the default
SECTION_GROUPBOX = 1

# constants for signals
SIGNAL_ACTIVATED = 10 # widget has received focus
SIGNAL_CLICKED = 101 # widget has been clicked
SIGNAL_TOGGLED = 102 # on/off widget has been toggled
SIGNAL_SELECTED = 151 # item in widget has been selected; handler must take index param
SIGNAL_FOCUS_IN = 191 # widget has received keyboard focus
SIGNAL_FOCUS_OUT = 195 # widget has lost keyboard focus
SIGNAL_LISTVIEWCHANGED = 201 # list view item has changed; handler must take item param
SIGNAL_TABLECHANGED = 301 # table cell text has changed; handler must take row, col params
SIGNAL_TEXTCHANGED = 401 # text in edit control has been changed
SIGNAL_EDITCHANGED = 450 # text in edit box has been changed
SIGNAL_ENTER = 490 # enter/return key has been pressed while widget has focus
SIGNAL_TABCHANGED = 501 # new tab has been selected; handler must take widget param
SIGNAL_WIDGETCHANGED = 901 # widget has been changed (not including above specific changes)
SIGNAL_CLOSING = 931 # widget close has been accepted
SIGNAL_HIDDEN = 951 # widget has been hidden

# these signal constants are for internal use only
SIGNAL_NOTIFIER = 801 # socket notifier has received an event notification
SIGNAL_QUERYCLOSE = 991 # widget is asking permission to close
SIGNAL_BEFOREQUIT = 999 # app is about to quit

# constants for action flags, used as keys
ACTION_FILENEW = 1
ACTION_FILEOPEN = 2
ACTION_FILESAVE = 4
ACTION_FILESAVEAS = 8
ACTION_FILECLOSE = 16
ACTION_VIEW = 240
ACTION_EDIT = 256
ACTION_REFRESH = 512
ACTION_ADD = 1024
ACTION_REMOVE = 2048
ACTION_APPLY = 8192
ACTION_COMMIT = 8288
ACTION_OK = 16384
ACTION_CANCEL = 32768
ACTION_PREFS = 41000
ACTION_ABOUT = 49152
ACTION_EXIT = 65536

# color constants -- we choose values to make hacks easier :)
COLORNAMES = ['BLACK', 'RED', 'BLUE', 'GREEN', 'YELLOW', 'WHITE', 'LIGHTGRAY', 'MAGENTA']
for color in COLORNAMES:
    setattr(sys.modules[__name__], 'COLOR_%s' % color, color)

# top window geometry constants
SIZE_NONE = 0
SIZE_CLIENTWRAP = 1
SIZE_MAXIMIZED = 2
SIZE_OFFSET = 4

MOVE_NONE = 0
MOVE_CENTER = 1

# Socket notifier constants
NOTIFY_READ = 0
NOTIFY_WRITE = 1

# Clean up namespace
del sys
