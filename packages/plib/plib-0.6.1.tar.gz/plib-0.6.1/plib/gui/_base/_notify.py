#!/usr/bin/env python
"""
Module NOTIFY -- Base for GUI Signal Emitters
Sub-Package GUI.BASE of Package PLIB -- Python GUI Framework
Copyright (C) 2008-2009 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

Defines an abstract base class for all signal-emitting GUI classes.
"""

from plib.gui.common import *

class _PNotifyBase(object):
    """
    Base class for objects that can send signals to notify other objects.
    """
    
    signal = None
    
    def connect_to(self, target):
        """ Connect our standard signal to the target; note that some
        other derived or mixin class must implement the setup_notify
        method. """
        
        if (self.signal is not None) and hasattr(self, 'setup_notify'):
            self.setup_notify(self.signal, target)
    
    def get_icon_filename(key):
        return pxfile(actiondict[key][0])
    get_icon_filename = staticmethod(get_icon_filename)
    
    def get_menu_str(key):
        return actiondict[key][1]
    get_menu_str = staticmethod(get_menu_str)
    
    def get_toolbar_str(key):
        return actiondict[key][1].replace('&', '')
    get_toolbar_str = staticmethod(get_toolbar_str)
    
    def get_accel_str(key):
        s = actiondict[key][1]
        i = s.find('&')
        if i > -1:
            return "+".join(["Alt", s[i + 1].upper()])
        else:
            return None
    get_accel_str = staticmethod(get_accel_str)
