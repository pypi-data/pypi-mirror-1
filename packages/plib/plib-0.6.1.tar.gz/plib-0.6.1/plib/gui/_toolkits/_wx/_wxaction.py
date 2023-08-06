#!/usr/bin/env python
"""
Module WXACTION -- Python wxWidgets Action Objects
Sub-Package GUI.TOOLKITS.WX of Package PLIB -- Python GUI Toolkits
Copyright (C) 2008-2009 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the wxWidgets GUI objects for handling user actions.
"""

import sys

import wx

from plib.gui._base import action

from _wxcommon import _PWxCommunicator

def scaled_bitmap(image, factor):
    if factor is not None:
        image = image.Scale(image.GetWidth() * factor, image.GetHeight() * factor)
    return wx.BitmapFromImage(image)

class PWxPopup(wx.Menu):
    """
    A customized wxWidgets popup menu class.
    """
    
    def __init__(self, mainwidget):
        self.mainwidget = mainwidget
        astyle = 0
        wx.Menu.__init__(self, "", astyle)

class PWxMenu(wx.MenuBar, action.PMenuBase):
    """
    A customized wxWidgets menu class.
    """
    
    popupclass = PWxPopup
    
    def __init__(self, mainwidget):
        astyle = 0
        wx.MenuBar.__init__(self, astyle)
        action.PMenuBase.__init__(self, mainwidget)
    
    def _add_popup(self, title, popup):
        self.Append(popup, title)
    
    def _add_popup_action(self, act, popup):
        item = wx.MenuItem(popup, act.id, act.menustr)
        item.SetBitmap(scaled_bitmap(act.image, act.menufactor))
        popup.AppendItem(item)

class PWxToolBar(wx.ToolBar, action.PToolBarBase):
    """
    A customized wxWidgets toolbar class.
    """
    
    def __init__(self, mainwidget):
        astyle = 0
        if mainwidget.show_labels:
            astyle = astyle | wx.TB_TEXT
        wx.ToolBar.__init__(self, mainwidget, style=astyle)
        action.PToolBarBase.__init__(self, mainwidget)
        self.Realize()
    
    def add_action(self, act):
        img = scaled_bitmap(act.image, act.toolbarfactor)
        if self.mainwin.show_labels:
            self.AddLabelTool(act.id, act.toolbarstr,
                img, shortHelp=act.toolbarstr)
        else:
            self.AddTool(act.id, img, shortHelpString=act.toolbarstr)
    
    def add_separator(self):
        self.AddSeparator()

class PWxAction(action.PActionBase, _PWxCommunicator):
    """
    A customized wxWidgets action class.
    """
    
    def __init__(self, key, mainwidget):
        self.image = wx.Image(self.get_icon_filename(key))
        self.menufactor = 0.5
        if mainwidget.large_icons:
            self.toolbarfactor = None
        else:
            self.toolbarfactor = 0.6875
        self.menustr = self.get_menu_str(key)
        self.toolbarstr = self.get_toolbar_str(key)
        self.accelstr = self.get_accel_str(key)
        self.id = wx.ID_HIGHEST + key
        action.PActionBase.__init__(self, key, mainwidget)
    
    # Need these three 'fake' widget methods to enable setup_notify mechanism
    def GetId(self):
        return self.id
    def Connect(self, *args):
        self.mainwin.Connect(*args)
    def Bind(self, event, target):
        self.mainwin.Bind(event, target, id=self.id)
    
    def enable(self, enabled):
        menu = self.mainwin.menu
        toolbar = self.mainwin.toolbar
        if menu is not None:
            menu.Enable(self.id, enabled)
        if toolbar is not None:
            toolbar.EnableTool(self.id, enabled)
