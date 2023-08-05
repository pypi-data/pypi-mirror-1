#!/usr/bin/env python
"""
Module TABWIDGET -- GUI Tab Widget
Sub-Package GUI.WIDGETS of Package PLIB -- Python GUI Framework
Copyright (C) 2008 by Peter A. Donis

Defines the widget classes for a tab widget.
"""

from plib.stdlib import baselist

from plib.gui.defs import *

class PTabWidgetBase(baselist):
    """
    Tab widget that looks like a Python list of 2-tuples (tab-title, widget).
    """
    
    def __init__(self, tabs=None):
        self.widgets = {}
        baselist.__init__(self, tabs)
    
    def _get_tabtitle(self, index):
        """ Placeholder for derived classes to implement. """
        raise NotImplementedError
    
    def _set_tabtitle(self, index, title):
        """ Placeholder for derived classes to implement. """
        raise NotImplementedError
    
    def _add_tab(self, index, title, widget):
        """ Placeholder for derived classes to implement. """
        raise NotImplementedError
    
    def _del_tab(self, index):
        """ Placeholder for derived classes to implement. """
        raise NotImplementedError
    
    def _get_data(self, index):
        return (self._get_tabtitle(index), self.widgets[index])
    
    def _set_data(self, index, value):
        """ This gets a little complicated because we have to delete the
        old tab at this index and insert a new one. """
        self._del_data(index)
        self._add_data(index, value)
    
    def _add_data(self, index, value):
        self._add_tab(index, value[0], value[1])
        self.widgets[index] = value[1]
    
    def _del_data(self, index):
        del self.widgets[index]
        self._del_tab(index)
    
    def current_index(self):
        """ Derived classes must override to return the currently selected tab index. """
        raise NotImplementedError
    
    def set_current_index(self, index):
        """ Placeholder for derived classes to implement. """
        raise NotImplementedError
    
    def current_title(self):
        return self[self.current_index()][0]
    
    def current_widget(self):
        return self[self.current_index()][1]
