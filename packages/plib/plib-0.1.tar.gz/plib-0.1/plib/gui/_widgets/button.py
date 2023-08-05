#!/usr/bin/env python
"""
Module BUTTON -- GUI Button Widgets
Sub-Package GUI.WIDGETS of Package PLIB -- Python GUI Framework
Copyright (C) 2008 by Peter A. Donis

Defines the widget classes for button widgets.
"""

from plib.gui.defs import *
from plib.gui._widgets import _signal

class PButtonBase(_signal._PNotifyControl):
    """ Base class for push button. """
    
    signal = SIGNAL_CLICKED
    
    def __init__(self, caption=None, pxname=None, target=None,
        geometry=None):
        
        if isinstance(caption, int):
            # 'caption' is actually an action key
            if pxname == "":
                pxname = caption
            caption = self.get_menu_str(caption)
        if isinstance(pxname, int):
            # 'pxname' is actually an action key
            pxname = self.get_icon_filename(pxname)
        if caption is not None:
            self.set_caption(caption)
        if pxname is not None:
            self.set_icon(pxname)
        _signal._PNotifyControl.__init__(self, target)
        if geometry is not None:
            self.set_geometry(*geometry)
    
    def set_caption(self, caption):
        """ Placeholder for derived classes to implement. """
        raise NotImplementedError
    
    def set_icon(self, pxname):
        """ Placeholder for derived classes to implement. """
        raise NotImplementedError
    
    def set_geometry(self, left, top, width, height):
        """ Placeholder for derived classes to implement. """
        raise NotImplementedError

class PCheckBoxBase(PButtonBase):
    """ Base class for checkbox. """
    
    signal = SIGNAL_TOGGLED
    
    def __init__(self, caption=None, pxname=None, tristate=False, target=None,
        geometry=None):
        
        PButtonBase.__init__(self, caption, pxname, target, geometry)
        if tristate:
            self.make_tristate()
    
    def make_tristate(self):
        """ Placeholder for derived classes to implement. """
        raise NotImplementedError
