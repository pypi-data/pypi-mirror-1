#!/usr/bin/env python
"""
Module QT4ACTION -- Python Qt 4 Action Objects
Sub-Package GUI.TOOLKITS.QT4 of Package PLIB -- Python GUI Toolkits
Copyright (C) 2008-2009 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the Qt 4 GUI objects for handling user actions.
"""

from PyQt4 import Qt as qt

from plib.gui._base import action

from _qt4common import _PQtCommunicator

class PQtMenu(qt.QMenuBar, action.PMenuBase):
    """
    A customized Qt menu class.
    """
    
    popupclass = qt.QMenu
    
    def __init__(self, mainwidget):
        qt.QMenuBar.__init__(self, mainwidget)
        action.PMenuBase.__init__(self, mainwidget)
        mainwidget.setMenuBar(self)
    
    def _add_popup(self, title, popup):
        popup.setTitle(title)
        self.addMenu(popup)
    
    def _add_popup_action(self, act, popup):
        popup.addAction(act)

class PQtToolBar(qt.QToolBar, action.PToolBarBase):
    """
    A customized Qt toolbar class.
    """
    
    def __init__(self, mainwidget):
        qt.QToolBar.__init__(self, mainwidget)
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

class PQtAction(qt.QAction, action.PActionBase, _PQtCommunicator):
    """
    A customized Qt action class.
    """
    
    def __init__(self, key, mainwidget):
        qt.QAction.__init__(self, mainwidget)
        self.setIcon(qt.QIcon(qt.QPixmap(self.get_icon_filename(key))))
        self.setText(qt.QString(self.get_menu_str(key)))
        self.setToolTip(qt.QString(self.get_toolbar_str(key)))
        s = self.get_accel_str(key)
        if s is not None:
            self.setShortcut(qt.QKeySequence(s))
        action.PActionBase.__init__(self, key, mainwidget)
    
    def enable(self, enabled):
        self.setEnabled(enabled)
