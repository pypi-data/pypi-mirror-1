#!/usr/bin/env python
"""
Module EDITCTRL -- GUI Editing Widgets
Sub-Package GUI.WIDGETS of Package PLIB -- Python GUI Framework
Copyright (C) 2008 by Peter A. Donis

Defines the widget classes for edit controls.
"""

from plib.gui.defs import *
from plib.gui._widgets import _signal

class PEditControlBase(_signal._PNotifyControl):
    """ Base class for edit control. """
    
    signal = SIGNAL_TEXTCHANGED
    
    def __init__(self, target=None, geometry=None):
        _signal._PNotifyControl.__init__(self, target)
        if geometry is not None:
            self.set_geometry(*geometry)
    
    def set_geometry(self, left, top, width, height):
        """ Placeholder for derived classes to implement. """
        raise NotImplementedError
