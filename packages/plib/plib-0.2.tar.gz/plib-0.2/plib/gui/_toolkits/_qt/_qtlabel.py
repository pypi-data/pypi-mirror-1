#!/usr/bin/env python
"""
Module QTLABEL -- Python Qt Text Label Widgets
Sub-Package GUI.TOOLKITS.QT of Package PLIB -- Python GUI Toolkits
Copyright (C) 2008 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the Qt GUI objects for text label widgets.
"""

import qt

from plib.gui._widgets import label

from _qtcommon import _PQtWidget

class PQtTextLabel(qt.QLabel, label.PTextLabelBase, _PQtWidget):
    
    def __init__(self, parent, text=None):
        qt.QLabel.__init__(self, parent)
        label.PTextLabelBase.__init__(self, text)
    
    def get_text(self):
        return str(self.text())
    
    def set_text(self, value):
        self.setText(value)
