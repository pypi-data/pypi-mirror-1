#!/usr/bin/env python
"""
Module KDEBUTTON -- Python KDE Button Widgets
Sub-Package GUI.TOOLKITS.KDE of Package PLIB -- Python GUI Toolkits
Copyright (C) 2008 by Peter A. Donis

This module contains the KDE GUI objects for button widgets.
"""

import qt
import kdeui

from plib.gui._widgets import button

from _kdecommon import _PKDEWidget

class _PKDEButtonMixin(object):
    
    def set_caption(self, caption):
        self.setText(caption)

class PKDEButton(kdeui.KPushButton, _PKDEWidget, _PKDEButtonMixin, button.PButtonBase):
    
    def __init__(self, parent, caption=None, pxname=None, target=None, geometry=None):
        kdeui.KPushButton.__init__(self, parent)
        self.setSizePolicy(qt.QSizePolicy.Fixed, qt.QSizePolicy.Fixed)
        button.PButtonBase.__init__(self, caption, pxname, target, geometry)
    
    def set_geometry(self, left, top, width, height):
        self.setGeometry(left, top, width, height)
        # KDE buttons don't appear to fully respect QSizePolicy.Fixed
        self.setMinimumSize(width, height)
    
    def set_icon(self, pxname):
        self.setIconSet(qt.QIconSet(qt.QPixmap(pxname)))

class PKDECheckBox(qt.QCheckBox, _PKDEWidget, _PKDEButtonMixin, button.PCheckBoxBase):
    
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
