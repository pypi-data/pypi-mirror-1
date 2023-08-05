#!/usr/bin/env python
"""
Module EDITCTRL -- GUI Editing Widgets
Sub-Package GUI.WIDGETS of Package PLIB -- Python GUI Framework
Copyright (C) 2008 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

Defines the widget classes for edit controls.
"""

from plib.gui.defs import *
from plib.gui._widgets import _control

class PEditControlBase(_control._PDialogControl):
    """ Base class for edit control. """
    
    signal = SIGNAL_TEXTCHANGED
