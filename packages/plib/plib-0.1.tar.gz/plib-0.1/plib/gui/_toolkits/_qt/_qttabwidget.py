#!/usr/bin/env python
"""
Module QTTABWIDGET -- Python Qt Tab Widget
Sub-Package GUI.TOOLKITS.QT of Package PLIB -- Python GUI Toolkits
Copyright (C) 2008 by Peter A. Donis

This module contains the Qt GUI objects for the tab widget.
"""

import qt

from plib.gui._widgets import tabwidget

from _qtcommon import _PQtCommunicator

class PQtTabWidget(qt.QTabWidget, tabwidget.PTabWidgetBase, _PQtCommunicator):
    
    def __init__(self, parent, tabs=None):
        qt.QTabWidget.__init__(self, parent)
        tabwidget.PTabWidgetBase.__init__(self, tabs)
    
    def count(self, value):
        """
        Method name collision, we want it to be the Python sequence
        count method here.
        """
        return tabwidget.PTabWidgetBase.count(self, value)
    
    def __len__(self):
        """ Let this method access the Qt tab widget count method. """
        return qt.QTabWidget.count(self)
    
    def _get_tabtitle(self, index):
        return str(self.tabLabel(self.widgets[index]))
    
    def _set_tabtitle(self, index, title):
        self.setTabLabel(self.widgets[index], str(title))
    
    def _add_tab(self, index, title, widget):
        self.insertTab(widget, str(title), index)
    
    def _del_tab(self, index):
        pass
    
    def current_index(self):
        return self.currentPageIndex()
    
    def set_current_index(self, index):
        self.setCurrentPage(index)
