#!/usr/bin/env python
"""
Module GTKTABWIDGET -- Python Gtk Tab Widget
Sub-Package GUI.TOOLKITS.GTK of Package PLIB -- Python GUI Toolkits
Copyright (C) 2008 by Peter A. Donis

This module contains the Gtk GUI objects for the tab widget.
"""

import pygtk
pygtk.require('2.0')
import gtk

from plib.gui.defs import *
from plib.gui._widgets import tabwidget

from _gtkcommon import _PGtkWidget

class PGtkTabWidget(gtk.Notebook, _PGtkWidget, tabwidget.PTabWidgetBase):
    
    def __init__(self, parent, tabs=None):
        gtk.Notebook.__init__(self)
        _PGtkWidget.__init__(self, parent, ALIGN_JUST)
        tabwidget.PTabWidgetBase.__init__(self, tabs)
    
    def __len__(self):
        return self.get_n_pages()
    
    def _get_tabtitle(self, index):
        return self.get_tab_label_text(self.widgets[index])
    
    def _set_tabtitle(self, index, title):
        self.set_tab_label_text(self.widgets[index], title)
    
    def _add_tab(self, index, title, widget):
        self.insert_page(widget, None, index)
        self.set_tab_label_text(widget, title)
        widget.show()
    
    def _del_tab(self, index):
        self.remove_page(index)
    
    def _add_widget(self, widget, x=0, y=0):
        pass
    
    def current_index(self):
        return self.get_current_page()
    
    def set_current_index(self, index):
        self.set_current_page(index)
