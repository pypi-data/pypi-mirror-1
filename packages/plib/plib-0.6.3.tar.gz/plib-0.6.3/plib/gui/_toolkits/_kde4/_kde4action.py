#!/usr/bin/env python
"""
Module KDE4ACTION -- Python KDE Action Objects
Sub-Package GUI.TOOLKITS.KDE of Package PLIB -- Python GUI Toolkits
Copyright (C) 2008-2010 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the KDE 4 GUI objects for handling user actions.
"""

from PyQt4 import Qt as qt
from PyKDE4 import kdeui

from plib.gui._base import action

from _kde4common import _PKDECommunicator, _PKDEWidgetBase

class PKDEMenu(kdeui.KMenuBar, _PKDEWidgetBase, action.PMenuBase):
    """
    A customized KDE menu class.
    """
    
    popupclass = kdeui.KMenu
    
    def __init__(self, mainwidget):
        kdeui.KMenuBar.__init__(self, mainwidget)
        action.PMenuBase.__init__(self, mainwidget)
        mainwidget.setMenuBar(self)
    
    def _add_popup(self, title, popup):
        popup.setTitle(title)
        self.addMenu(popup)
    
    def _add_popup_action(self, act, popup):
        popup.addAction(act)

class PKDEToolBar(kdeui.KToolBar, _PKDEWidgetBase, action.PToolBarBase):
    """
    A customized KDE toolbar class.
    """
    
    def __init__(self, mainwidget):
        kdeui.KToolBar.__init__(self, mainwidget)
        if mainwidget.large_icons:
            sz = self.iconSize()
            w, h = map(lambda i: i * 3/2, (sz.width(), sz.height()))
            self.setIconSize(qt.QSize(w, h))
        if mainwidget.show_labels:
            style = qt.Qt.ToolButtonTextUnderIcon
        else:
            style = qt.Qt.ToolButtonIconOnly
        self.setToolButtonStyle(style)
        action.PToolBarBase.__init__(self, mainwidget)
        mainwidget.addToolBar(self)
    
    def add_action(self, act):
        self.addAction(act)
    
    def add_separator(self):
        self.addSeparator()

class PKDEAction(kdeui.KAction, _PKDECommunicator, action.PActionBase):
    """
    A customized KDE action class.
    """
    
    def __init__(self, key, mainwidget):
        kdeui.KAction.__init__(self, mainwidget)
        self.setIcon(kdeui.KIcon(qt.QIcon(qt.QPixmap(self.get_icon_filename(key)))))
        self.setText(qt.QString(self.get_menu_str(key)))
        self.setToolTip(qt.QString(self.get_toolbar_str(key)))
        s = self.get_accel_str(key)
        if s is not None:
            self.setShortcut(qt.QKeySequence(s))
        action.PActionBase.__init__(self, key, mainwidget)
    
    def enable(self, enabled):
        self.setEnabled(enabled)
