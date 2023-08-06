#!/usr/bin/env python
"""
Module QTEDITCTRL -- Python Qt Editing Widgets
Sub-Package GUI.TOOLKITS.QT of Package PLIB -- Python GUI Toolkits
Copyright (C) 2008-2010 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the Qt GUI objects for edit controls.
"""

import qt

from plib.gui._widgets import editctrl

from _qtcommon import _PQtWidget

class _PQtEditMixin(object):
    
    fn_get_text = 'str_text'
    fn_set_text = 'setText'
    
    fn_get_readonly = 'isReadOnly'
    fn_set_readonly = 'setReadOnly'
    
    def str_text(self):
        return str(self.text())

class PQtEditBox(qt.QLineEdit, _PQtWidget, _PQtEditMixin, editctrl.PEditBoxBase):
    
    widget_class = qt.QLineEdit
    
    def __init__(self, parent, target=None, geometry=None, expand=True):
        qt.QLineEdit.__init__(self, parent)
        if expand:
            self._horiz = qt.QSizePolicy.MinimumExpanding
        else:
            self._horiz = qt.QSizePolicy.Fixed
        self.setSizePolicy(self._horiz, qt.QSizePolicy.Fixed)
        editctrl.PEditBoxBase.__init__(self, target, geometry)
    
    def set_width(self, width):
        self.resize(width, self.height())
        # Qt line edits don't seem to fully respect qt.QSizePolicy.Fixed
        if self._horiz == qt.QSizePolicy.Fixed:
            self.setMaximumWidth(width)
        elif self._horiz == qt.QSizePolicy.MinimumExpanding:
            self.setMinimumWidth(width)

class PQtEditControl(qt.QTextEdit, _PQtWidget, _PQtEditMixin, editctrl.PEditControlBase):
    
    widget_class = qt.QTextEdit
    
    def __init__(self, parent, target=None, geometry=None, scrolling=False):
        qt.QTextEdit.__init__(self, parent)
        self.setTextFormat(qt.Qt.PlainText)
        if scrolling:
            self.setWordWrap(qt.QTextEdit.NoWrap)
        editctrl.PEditControlBase.__init__(self, target, geometry)
    
    def set_width(self, width):
        self.resize(width, self.height())
        # Qt text edits don't seem to fully respect qt.QSizePolicy.MinimumExpanding
        self.setMinimumWidth(width)
    
    def set_height(self, height):
        self.resize(self.width(), height)
        # Qt text edits don't seem to fully respect qt.QSizePolicy.MinimumExpanding
        self.setMinimumHeight(height)
