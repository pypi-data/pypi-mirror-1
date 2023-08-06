#!/usr/bin/env python
"""
Module KDEACTION -- Python KDE Action Objects
Sub-Package GUI.TOOLKITS.KDE of Package PLIB -- Python GUI Toolkits
Copyright (C) 2008-2009 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the KDE GUI objects for handling user actions.
"""

import qt
import kdeui

from plib.gui._base import action

from _kdecommon import _PKDECommunicator

class PKDEMenu(kdeui.KMenuBar, action.PMenuBase):
    """
    A customized KDE menu class.
    """
    
    popupclass = kdeui.KPopupMenu
    
    def __init__(self, mainwidget):
        kdeui.KMenuBar.__init__(self, mainwidget, "Main Menu")
        action.PMenuBase.__init__(self, mainwidget)
    
    def _add_popup(self, title, popup):
        self.insertItem(title, popup)
    
    def _add_popup_action(self, act, popup):
        act.addTo(popup)

class PKDEToolBar(kdeui.KToolBar, action.PToolBarBase):
    """
    A customized KDE toolbar class.
    """
    
    def __init__(self, mainwidget):
        self._sep = False
        kdeui.KToolBar.__init__(self, mainwidget, "Main Toolbar")
        # This has to be done here instead of in KMainWindow (unlike Qt)
        # FIXME: How to do large icons in KDE?
        #self.setFullSize(mainwidget.large_icons)
        if mainwidget.show_labels:
            it = kdeui.KToolBar.IconTextBottom
        else:
            it = kdeui.KToolBar.IconOnly
        self.setIconText(it)
        action.PToolBarBase.__init__(self, mainwidget)
        #FIXME: Why is this necessary in KDE but not in Qt?
        mainwidget.addDockWindow(self)
    
    def add_action(self, act):
        if self._sep:
            self.insertLineSeparator(act.key - 1, act.key - 1)
            self._sep = False
        act.addTo(self)
    
    def add_separator(self):
        #self.addSeparator()
        self._sep = True

class PKDEAction(kdeui.KAction, action.PActionBase, _PKDECommunicator):
    """
    A customized KDE action class.
    """
    
    def __init__(self, key, mainwidget):
        kdeui.KAction.__init__(self, mainwidget)
        self.setIconSet(qt.QIconSet(qt.QPixmap(self.get_icon_filename(key))))
        self.setText(qt.QString(self.get_menu_str(key)))
        self.setShortcutText(qt.QString(self.get_toolbar_str(key)))
        s = self.get_accel_str(key)
        if s is not None:
            self.setAccel(qt.QKeySequence(s))
        action.PActionBase.__init__(self, key, mainwidget)
    
    def addTo(self, widget):
        self.plug(widget, self.key)
    
    def enable(self, enabled):
        self.setEnabled(enabled)
