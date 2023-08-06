#!/usr/bin/env python
"""
Module WXEDITCTRL -- Python wxWidgets Editing Widgets
Sub-Package GUI.TOOLKITS.WX of Package PLIB -- Python GUI Toolkits
Copyright (C) 2008-2009 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the wxWidgets GUI objects for edit controls.
"""

import wx

from plib.gui.defs import *
from plib.gui._widgets import editctrl

from _wxcommon import _PWxWidget

class _PWxEditBase(wx.TextCtrl, _PWxWidget):
    
    def __init__(self, parent):
        wx.TextCtrl.__init__(self, parent, style=self._style)
    
    def _get_text(self):
        return self.GetValue()
    
    def _set_text(self, value):
        self.SetValue(value)
    
    edit_text = property(_get_text, _set_text)
    
    def _get_readonly(self):
        return not self.IsEditable()
    
    def _set_readonly(self, value):
        self.SetEditable(not value)
    
    readonly = property(_get_readonly, _set_readonly)

class PWxEditBox(_PWxEditBase, editctrl.PEditBoxBase):
    
    _style = wx.TE_PROCESS_ENTER
    
    def __init__(self, parent, target=None, geometry=None, expand=True):
        self._expand = False
        if expand:
            self._align = ALIGN_JUST
        else:
            self._align = ALIGN_LEFT
        _PWxEditBase.__init__(self, parent)
        editctrl.PEditBoxBase.__init__(self, target, geometry)

class PWxEditControl(_PWxEditBase, editctrl.PEditControlBase):
    
    _style = wx.TE_MULTILINE | wx.TE_PROCESS_TAB
    
    def __init__(self, parent, target=None, geometry=None, scrolling=False):
        self._expand = True
        self._align = ALIGN_JUST
        if scrolling:
            self._style = self._style | wx.VSCROLL | wx.HSCROLL | wx.TE_DONTWRAP
        _PWxEditBase.__init__(self, parent)
        editctrl.PEditControlBase.__init__(self, target, geometry)
