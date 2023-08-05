#!/usr/bin/env python
"""
Module QTBUTTON -- Python Qt Button Widgets
Sub-Package GUI.TOOLKITS.QT of Package PLIB -- Python GUI Toolkits
Copyright (C) 2008 by Peter A. Donis

This module contains the Qt GUI objects for button widgets.
"""

import qt

from plib.gui._widgets import button

from _qtcommon import _PQtWidget

class _PQtButtonMixin(object):
    
    def set_caption(self, caption):
        self.setText(caption)

class PQtButton(qt.QPushButton, _PQtWidget, _PQtButtonMixin, button.PButtonBase):
    
    def __init__(self, parent, caption=None, pxname=None, target=None, geometry=None):
        qt.QPushButton.__init__(self, parent)
        self.setSizePolicy(qt.QSizePolicy.Fixed, qt.QSizePolicy.Fixed)
        button.PButtonBase.__init__(self, caption, pxname, target, geometry)
    
    def set_icon(self, pxname):
        self.setIconSet(qt.QIconSet(qt.QPixmap(pxname)))
    
    def set_geometry(self, left, top, width, height):
        self.setGeometry(left, top, width, height)
        # Qt buttons don't appear to fully respect QSizePolicy.Fixed
        self.setMinimumSize(width, height)

class PQtCheckBox(qt.QCheckBox, _PQtWidget, _PQtButtonMixin, button.PCheckBoxBase):
    
    def __init__(self, parent, caption=None, pxname=None, tristate=False, target=None, geometry=None):
        qt.QCheckBox.__init__(self, parent)
        self.setSizePolicy(qt.QSizePolicy.Fixed, qt.QSizePolicy.Fixed)
        button.PCheckBoxBase.__init__(self, caption, pxname, tristate, target, geometry)
    
    def set_icon(self, pxname):
        # FIXME: pixmaps on checkboxes?
        pass
    
    def make_tristate(self):
        self.setTriState(True)
    
    def _get_checked(self):
        return self.isChecked()
    
    def _set_checked(self, value):
        return self.setChecked(value)
    
    checked = property(_get_checked, _set_checked)
