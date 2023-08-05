#!/usr/bin/env python
"""
Module KDEEDITCTRL -- Python KDE Editing Widgets
Sub-Package GUI.TOOLKITS.KDE of Package PLIB -- Python GUI Toolkits
Copyright (C) 2008 by Peter A. Donis

This module contains the KDE GUI objects for edit controls.
"""

import qt
import kdeui

from plib.gui.defs import *
from plib.gui._widgets import editctrl

from _kdecommon import _PKDEWidget

class _PKDEEditMixin(object):
    
    def _get_text(self):
        return str(self.text())
    
    def _set_text(self, value):
        self.setText(value)
    
    edit_text = property(_get_text, _set_text)
    
    def _get_readonly(self):
        return self.isReadOnly()
    
    def _set_readonly(self, value):
        self.setReadOnly(value)
        # KDE forces background to gray on readonly as well as disabled, fixup here
        if value:
            self.setPaletteBackgroundColor(qt.QColor('white'))
    
    readonly = property(_get_readonly, _set_readonly)

class PKDEEditBox(kdeui.KLineEdit, _PKDEWidget, editctrl.PEditControlBase, _PKDEEditMixin):
    
    def __init__(self, parent, target=None, geometry=None, expand=True):
        kdeui.KLineEdit.__init__(self, parent)
        if expand:
            self._horiz = qt.QSizePolicy.MinimumExpanding
        else:
            self._horiz = qt.QSizePolicy.Fixed
        self.setSizePolicy(self._horiz, qt.QSizePolicy.Fixed)
        editctrl.PEditControlBase.__init__(self, target, geometry)
    
    def set_geometry(self, left, top, width, height):
        self.setGeometry(left, top, width, height)
        # KDE edit controls don't seem to fully respect qt.QSizePolicy.Fixed
        if self._horiz == qt.QSizePolicy.Fixed:
            self.setMaximumWidth(width)

class PKDEEditControl(kdeui.KTextEdit, _PKDEWidget, editctrl.PEditControlBase, _PKDEEditMixin):
    
    def __init__(self, parent, target=None, geometry=None, scrolling=False):
        kdeui.KTextEdit.__init__(self, parent)
        self.setTextFormat(qt.Qt.PlainText)
        if scrolling:
            self.setWordWrap(qt.QTextEdit.NoWrap)
        editctrl.PEditControlBase.__init__(self, target, geometry)
