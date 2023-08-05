#!/usr/bin/env python
"""
Module GTKLABEL -- Python Gtk Text Label Widgets
Sub-Package GUI.TOOLKITS.GTK of Package PLIB -- Python GUI Toolkits
Copyright (C) 2008 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the Gtk GUI objects for text label widgets.
"""

import pygtk
pygtk.require('2.0')
import gtk

from plib.gui._widgets import label

from _gtkcommon import _PGtkWidget

class PGtkTextLabel(gtk.Label, label.PTextLabelBase, _PGtkWidget):
    
    def __init__(self, parent, text=None):
        gtk.Label.__init__(self)
        label.PTextLabelBase.__init__(self, text)
    
    # gtk.Label already has get_text and set_text methods
