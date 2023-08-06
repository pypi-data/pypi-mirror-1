#!/usr/bin/env python
"""
Module KDEEDITCTRL -- Python KDE Editing Widgets
Sub-Package GUI.TOOLKITS.KDE of Package PLIB -- Python GUI Toolkits
Copyright (C) 2008-2010 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the KDE GUI objects for edit controls.
"""

import qt
import kdeui

#from plib.gui.defs import *
from plib.gui._widgets import editctrl

from _kdecommon import _PKDEWidget

class _PKDEEditMixin(object):
    
    fn_get_text = 'str_text'
    fn_set_text = 'setText'
    
    fn_get_readonly = 'isReadOnly'
    fn_set_readonly = 'set_readonly_and_color'
    
    def str_text(self):
        return str(self.text())
    
    def set_readonly_and_color(self, value):
        if value:
            color = self.paletteBackgroundColor()
        self.setReadOnly(value)
        if value:
            # KDE forces background to disabled color on readonly as well as disabled, fixup here
            self.setPaletteBackgroundColor(color)

class PKDEEditBox(kdeui.KLineEdit, _PKDEWidget, _PKDEEditMixin, editctrl.PEditBoxBase):
    
    widget_class = kdeui.KLineEdit
    
    def __init__(self, parent, target=None, geometry=None, expand=True):
        kdeui.KLineEdit.__init__(self, parent)
        if expand:
            self._horiz = qt.QSizePolicy.MinimumExpanding
        else:
            self._horiz = qt.QSizePolicy.Fixed
        self.setSizePolicy(self._horiz, qt.QSizePolicy.Fixed)
        editctrl.PEditBoxBase.__init__(self, target, geometry)
    
    def set_width(self, width):
        self.resize(width, self.height())
        # KDE line edits don't seem to fully respect qt.QSizePolicy.Fixed
        if self._horiz == qt.QSizePolicy.Fixed:
            self.setMaximumWidth(width)
        elif self._horiz == qt.QSizePolicy.MinimumExpanding:
            self.setMinimumWidth(width)

class PKDEEditControl(kdeui.KTextEdit, _PKDEWidget, _PKDEEditMixin, editctrl.PEditControlBase):
    
    widget_class = kdeui.KTextEdit
    
    def __init__(self, parent, target=None, geometry=None, scrolling=False):
        kdeui.KTextEdit.__init__(self, parent)
        self.setTextFormat(qt.Qt.PlainText)
        if scrolling:
            self.setWordWrap(qt.QTextEdit.NoWrap)
        editctrl.PEditControlBase.__init__(self, target, geometry)
    
    def set_width(self, width):
        self.resize(width, self.height())
        # KDE text edits don't seem to fully respect qt.QSizePolicy.MinimumExpanding
        self.setMinimumWidth(width)
    
    def set_height(self, height):
        self.resize(self.width(), height)
        # KDE text edits don't seem to fully respect qt.QSizePolicy.MinimumExpanding
        self.setMinimumHeight(height)
