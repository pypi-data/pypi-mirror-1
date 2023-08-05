#!/usr/bin/env python
"""
Module KDELABEL -- Python KDE Text Label Widgets
Sub-Package GUI.TOOLKITS.KDE of Package PLIB -- Python GUI Toolkits
Copyright (C) 2008 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the KDE GUI objects for text label widgets.
"""

import kdeui

from plib.gui._widgets import label

from _kdecommon import _PKDEWidget

class PKDETextLabel(kdeui.KStatusBarLabel, label.PTextLabelBase, _PKDEWidget):
    
    def __init__(self, parent, text=None):
        kdeui.KStatusBarLabel.__init__(self, "", 0, parent)
        label.PTextLabelBase.__init__(self, text)
    
    def get_text(self):
        return str(self.text())
    
    def set_text(self, value):
        self.setText(value)
