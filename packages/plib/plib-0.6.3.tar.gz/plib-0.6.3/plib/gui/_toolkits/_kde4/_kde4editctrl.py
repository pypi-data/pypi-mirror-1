#!/usr/bin/env python
"""
Module KDE4EDITCTRL -- Python KDE Editing Widgets
Sub-Package GUI.TOOLKITS.KDE of Package PLIB -- Python GUI Toolkits
Copyright (C) 2008-2010 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the KDE 4 GUI objects for edit controls.
"""

from PyQt4 import Qt as qt
from PyKDE4 import kdeui

#from plib.gui.defs import *
from plib.gui._widgets import editctrl

from _kde4common import _PKDEWidget

class _PKDEEditMixin(object):
    
    fn_get_readonly = 'isReadOnly'
    fn_set_readonly = 'set_readonly_and_color'
    
    def set_readonly_and_color(self, value):
        if value and not self.isReadOnly():
            # KDE forces background to gray on readonly as well as disabled, fixup here
            palette = qt.QPalette(self.palette())
            palette.setColor(self.backgroundRole(), palette.color(qt.QPalette.Active, qt.QPalette.Base))
            self.setPalette(palette)
        self.setReadOnly(value)

class PKDEEditBox(kdeui.KLineEdit, _PKDEWidget, _PKDEEditMixin, editctrl.PEditBoxBase):
    
    fn_get_text = 'str_text'
    fn_set_text = 'setText'
    
    widget_class = kdeui.KLineEdit
    
    def __init__(self, parent, target=None, geometry=None, expand=True):
        kdeui.KLineEdit.__init__(self, parent)
        if expand:
            self._horiz = qt.QSizePolicy.MinimumExpanding
        else:
            self._horiz = qt.QSizePolicy.Fixed
        self.setSizePolicy(self._horiz, qt.QSizePolicy.Fixed)
        editctrl.PEditBoxBase.__init__(self, target, geometry)
    
    def str_text(self):
        return str(self.text())
    
    def set_width(self, width):
        self.resize(width, self.height())
        # KDE line edits don't seem to fully respect qt.QSizePolicy.Fixed
        if self._horiz == qt.QSizePolicy.Fixed:
            self.setMaximumWidth(width)
        elif self._horiz == qt.QSizePolicy.MinimumExpanding:
            self.setMinimumWidth(width)

class PKDEEditControl(kdeui.KTextEdit, _PKDEWidget, _PKDEEditMixin, editctrl.PEditControlBase):
    
    fn_get_text = 'str_plaintext'
    fn_set_text = 'setPlainText'
    
    widget_class = kdeui.KTextEdit
    
    def __init__(self, parent, target=None, geometry=None, scrolling=False):
        kdeui.KTextEdit.__init__(self, parent)
        if scrolling:
            self.setLineWrapMode(qt.QTextEdit.NoWrap)
        editctrl.PEditControlBase.__init__(self, target, geometry)
    
    def str_plaintext(self):
        return str(self.toPlainText())
    
    def set_width(self, width):
        self.resize(width, self.height())
        # KDE text edits don't seem to fully respect qt.QSizePolicy.MinimumExpanding
        self.setMinimumWidth(width)
    
    def set_height(self, height):
        self.resize(self.width(), height)
        # KDE text edits don't seem to fully respect qt.QSizePolicy.MinimumExpanding
        self.setMinimumHeight(height)
