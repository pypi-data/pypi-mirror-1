#!/usr/bin/env python
"""
Module QTEDITCTRL -- Python Qt Editing Widgets
Sub-Package GUI.TOOLKITS.QT of Package PLIB -- Python GUI Toolkits
Copyright (C) 2008 by Peter A. Donis

This module contains the Qt GUI objects for edit controls.
"""

import qt

from plib.gui._widgets import editctrl

from _qtcommon import _PQtWidget

class _PQtEditMixin(object):
    
    def _get_text(self):
        return str(self.text())
    
    def _set_text(self, value):
        self.setText(value)
    
    edit_text = property(_get_text, _set_text)
    
    def _get_readonly(self):
        return self.isReadOnly()
    
    def _set_readonly(self, value):
        self.setReadOnly(value)
    
    readonly = property(_get_readonly, _set_readonly)

class PQtEditBox(qt.QLineEdit, _PQtWidget, editctrl.PEditControlBase, _PQtEditMixin):
    
    def __init__(self, parent, target=None, geometry=None, expand=True):
        qt.QLineEdit.__init__(self, parent)
        if expand:
            self._horiz = qt.QSizePolicy.MinimumExpanding
        else:
            self._horiz = qt.QSizePolicy.Fixed
        self.setSizePolicy(self._horiz, qt.QSizePolicy.Fixed)
        editctrl.PEditControlBase.__init__(self, target, geometry)
    
    def set_geometry(self, left, top, width, height):
        self.setGeometry(left, top, width, height)
        # Qt edit controls don't seem to fully respect qt.QSizePolicy.Fixed
        if self._horiz == qt.QSizePolicy.Fixed:
            self.setMaximumWidth(width)

class PQtEditControl(qt.QTextEdit, _PQtWidget, editctrl.PEditControlBase, _PQtEditMixin):
    
    def __init__(self, parent, target=None, geometry=None, scrolling=False):
        qt.QTextEdit.__init__(self, parent)
        self.setTextFormat(qt.Qt.PlainText)
        if scrolling:
            self.setWordWrap(qt.QTextEdit.NoWrap)
        editctrl.PEditControlBase.__init__(self, target, geometry)
