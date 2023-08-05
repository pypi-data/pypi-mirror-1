#!/usr/bin/env python
"""
Module Action -- GUI Action Classes
Sub-Package GUI.BASE of Package PLIB -- Python GUI Framework
Copyright (C) 2008 by Peter A. Donis

Defines the classes that handle user actions.
"""

from plib.gui.defs import *
from plib.gui.common import *

from plib.gui._base import _notify

class PActionBase(_notify._PNotifyBase):
    """
    Base class for GUI action objects.
    
    Uses above globals to determine action pixmaps and labels; the
    globals can be modified as long as it's done before any actions are
    instantiated (if the actions are being created by a PMainWindow, which
    is the intended use case, the globals must be modified either before
    PMainWindow.__init__ is called (because the actions are created inside
    the constructor), or inside an overridden PMainWindow.createactions.
    """
    
    signal = SIGNAL_ACTIVATED
    
    def __init__(self, key, mainwidget):
        self.key = key
        self.mainwin = mainwidget
        
        # Add ourself to main menu and toolbar if they exist
        if mainwidget.menu is not None:
            mainwidget.menu.add_action(self)
        if mainwidget.toolbar is not None:
            mainwidget.toolbar.add_action(self)
    
    def enable(self, enabled):
        """ Placeholder for derived classes to implement """
        pass

class _PGUIBase(object):
    """
    Base class for GUI menus and toolbars to add actions.
    """
    
    def __init__(self, mainwidget):
        self.mainwin = mainwidget
    
    def add_action(self, action):
        """ Placeholder for derived classes to implement """
        pass

class PMenuBase(_PGUIBase):
    """
    Base class for GUI menu.
    """
    
    popupclass = None
    
    def __init__(self, mainwidget):
        _PGUIBase.__init__(self, mainwidget)
        self.popups = {}
    
    def _add_popup(self, title, popup):
        """ Placeholder for derived classes to implement. """
        pass
    
    def add_popup(self, title):
        if self.popupclass is not None:
            popup = self.popupclass(self.mainwin)
            self._add_popup(title, popup)
            self.popups[title] = popup
    
    def get_popup(self, title):
        if title in self.popups:
            return self.popups[title]
        else:
            return None
    
    def _add_popup_action(self, action, popup):
        """ Placeholder for derived classes to implement """
        pass
    
    def add_action(self, action):
        for title in menukeydict:
            if action.key in menukeydict[title]:
                if self.get_popup(title) is None:
                    self.add_popup(title)
                self._add_popup_action(action, self.popups[title])

class PToolBarBase(_PGUIBase):
    """
    Base class for GUI toolbar.
    """
    
    def add_separator(self):
        """ Placeholder for derived classes to implement """
        pass
