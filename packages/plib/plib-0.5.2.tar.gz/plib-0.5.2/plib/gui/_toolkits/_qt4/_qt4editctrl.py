#!/usr/bin/env python
"""
Module QT4EDITCTRL -- Python Qt 4 Editing Widgets
Sub-Package GUI.TOOLKITS.QT4 of Package PLIB -- Python GUI Toolkits
Copyright (C) 2008 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the Qt 4 GUI objects for edit controls.
"""

from PyQt4 import Qt as qt

from plib.gui._widgets import editctrl

from _qt4common import _PQtWidget

class _PQtEditMixin(object):
    
    def _get_readonly(self):
        return self.isReadOnly()
    
    def _set_readonly(self, value):
        self.setReadOnly(value)
    
    readonly = property(_get_readonly, _set_readonly)

class PQtEditBox(qt.QLineEdit, _PQtWidget, editctrl.PEditBoxBase, _PQtEditMixin):
    
    def __init__(self, parent, target=None, geometry=None, expand=True):
        qt.QLineEdit.__init__(self, parent)
        if expand:
            self._horiz = qt.QSizePolicy.MinimumExpanding
        else:
            self._horiz = qt.QSizePolicy.Fixed
        self.setSizePolicy(self._horiz, qt.QSizePolicy.Fixed)
        editctrl.PEditBoxBase.__init__(self, target, geometry)
    
    def _get_text(self):
        return str(self.text())
    
    def _set_text(self, value):
        self.setText(value)
    
    edit_text = property(_get_text, _set_text)
    
    def set_width(self, width):
        self.resize(width, self.height())
        # Qt line edits don't seem to fully respect qt.QSizePolicy.Fixed
        if self._horiz == qt.QSizePolicy.Fixed:
            self.setMaximumWidth(width)
        elif self._horiz == qt.QSizePolicy.MinimumExpanding:
            self.setMinimumWidth(width)

class PQtEditControl(qt.QTextEdit, _PQtWidget, editctrl.PEditControlBase, _PQtEditMixin):
    
    def __init__(self, parent, target=None, geometry=None, scrolling=False):
        qt.QTextEdit.__init__(self, parent)
        if scrolling:
            self.setLineWrapMode(qt.QTextEdit.NoWrap)
        editctrl.PEditControlBase.__init__(self, target, geometry)
    
    def _get_text(self):
        return str(self.toPlainText())
    
    def _set_text(self, value):
        self.setPlainText(value)
    
    edit_text = property(_get_text, _set_text)
    
    def set_width(self, width):
        self.resize(width, self.height())
        # Qt text edits don't seem to fully respect qt.QSizePolicy.MinimumExpanding
        self.setMinimumWidth(width)
    
    def set_height(self, height):
        self.resize(self.width(), height)
        # Qt text edits don't seem to fully respect qt.QSizePolicy.MinimumExpanding
        self.setMinimumHeight(height)
