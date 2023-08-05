#!/usr/bin/env python
"""
Module KDETABWIDGET -- Python KDE Tab Widget
Sub-Package GUI.TOOLKITS.KDE of Package PLIB -- Python GUI Toolkits
Copyright (C) 2008 by Peter A. Donis

This module contains the KDE GUI objects for the tab widget.
"""

import kdeui

from plib.gui._widgets import tabwidget

from _kdecommon import _PKDECommunicator

class PKDETabWidget(kdeui.KTabWidget, tabwidget.PTabWidgetBase, _PKDECommunicator):
    
    def __init__(self, parent, tabs=None):
        kdeui.KTabWidget.__init__(self, parent)
        tabwidget.PTabWidgetBase.__init__(self, tabs)
    
    def count(self, value):
        """
        Method name collision, we want it to be the Python sequence
        count method here.
        """
        return tabwidget.PTabWidgetBase.count(self, value)
    
    def __len__(self):
        """ Let this method access the KDE tab widget count method. """
        return kdeui.KTabWidget.count(self)
    
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
