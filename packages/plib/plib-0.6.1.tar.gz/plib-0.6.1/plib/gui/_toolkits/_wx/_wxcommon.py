#!/usr/bin/env python
"""
Module WXCOMMON -- Python wxWidgets Common Objects
Sub-Package GUI.TOOLKITS.WX of Package PLIB -- Python GUI Toolkits
Copyright (C) 2008-2009 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the wxWidgets GUI common objects.
"""

import wx
import wx.grid
from wx.lib.evtmgr import eventManager
from wx.lib.newevent import NewEvent

from plib.gui.defs import *

_wxstockids = {
    ACTION_FILENEW: wx.ID_NEW,
    ACTION_FILEOPEN: wx.ID_OPEN,
    ACTION_FILESAVE: wx.ID_SAVE,
    ACTION_FILESAVEAS: wx.ID_SAVEAS,
    ACTION_FILECLOSE: wx.ID_CLOSE,
    ACTION_EDIT: wx.ID_EDIT,
    ACTION_REFRESH: wx.ID_REFRESH,
    ACTION_ADD: wx.ID_ADD,
    ACTION_REMOVE: wx.ID_REMOVE,
    ACTION_APPLY: wx.ID_APPLY,
    ACTION_OK: wx.ID_OK,
    ACTION_CANCEL: wx.ID_CANCEL,
    ACTION_PREFS: wx.ID_PREFERENCES,
    ACTION_ABOUT: wx.ID_ABOUT,
    ACTION_EXIT: wx.ID_EXIT }

_wxalignmap = {
    ALIGN_LEFT: None,
    ALIGN_CENTER: None,
    ALIGN_RIGHT: None }

_wxicons = {
    MBOX_INFO: wx.ICON_INFORMATION,
    MBOX_WARN: wx.ICON_EXCLAMATION,
    MBOX_ERROR: wx.ICON_ERROR,
    MBOX_QUERY: wx.ICON_QUESTION }

_wxfontfamilies = {
    wx.FONTFAMILY_ROMAN: ["Courier New", "Times New Roman"],
    wx.FONTFAMILY_SWISS: ["Arial", "Verdana"] }

# Define our own custom event for SIGNAL_CLOSING
ClosingEvent, EVT_CLOSING = NewEvent()

_wxcustommap = {
    SIGNAL_CLOSING: ClosingEvent }

_wxeventmap = {
    SIGNAL_ACTIVATED: wx.EVT_MENU,
    SIGNAL_CLICKED: wx.EVT_BUTTON,
    SIGNAL_TOGGLED: wx.EVT_CHECKBOX,
    SIGNAL_SELECTED: wx.EVT_COMBOBOX,
    SIGNAL_FOCUS_IN: wx.EVT_SET_FOCUS,
    SIGNAL_FOCUS_OUT: wx.EVT_KILL_FOCUS,
    SIGNAL_LISTVIEWCHANGED: wx.EVT_TREE_SEL_CHANGED,
    SIGNAL_TABLECHANGED: wx.grid.EVT_GRID_CELL_CHANGE,
    SIGNAL_TEXTCHANGED: wx.EVT_TEXT,
    SIGNAL_EDITCHANGED: wx.EVT_TEXT,
    SIGNAL_ENTER: wx.EVT_TEXT_ENTER,
    SIGNAL_TABCHANGED: wx.EVT_NOTEBOOK_PAGE_CHANGED,
    SIGNAL_CLOSING: EVT_CLOSING,
    SIGNAL_HIDDEN: wx.EVT_WINDOW_DESTROY,
    SIGNAL_QUERYCLOSE: wx.EVT_CLOSE,
    SIGNAL_BEFOREQUIT: wx.EVT_WINDOW_DESTROY }

# 'Wrapper' functions for certain events to repackage parameters

def wx_plain_wrapper(self, target):
    def wrapper(event):
        target()
    return wrapper

def wx_selected_wrapper(self, target):
    def wrapper(event):
        target(self.GetSelection())
    return wrapper

def wx_listviewchanged_wrapper(self, target):
    def wrapper(event):
        item = self.GetItemPyData(event.GetItem())
        # Hack to filter out events fired too soon by some Wx versions
        if item is not None:
            target(item)
    return wrapper

def wx_tablechanged_wrapper(self, target):
    def wrapper(event):
        target(event.GetRow(), event.GetCol())
    return wrapper

def wx_tabchanged_wrapper(self, target):
    def wrapper(event):
        target(self._items[event.GetSelection()])
    return wrapper

_wxwrappermap = {
    SIGNAL_ACTIVATED: wx_plain_wrapper,
    SIGNAL_CLICKED: wx_plain_wrapper,
    SIGNAL_TOGGLED: wx_plain_wrapper,
    SIGNAL_SELECTED: wx_selected_wrapper,
    SIGNAL_FOCUS_IN: wx_plain_wrapper,
    SIGNAL_FOCUS_OUT: wx_plain_wrapper,
    SIGNAL_LISTVIEWCHANGED: wx_listviewchanged_wrapper,
    SIGNAL_TABLECHANGED: wx_tablechanged_wrapper,
    SIGNAL_TEXTCHANGED: wx_plain_wrapper,
    SIGNAL_EDITCHANGED: wx_plain_wrapper,
    SIGNAL_ENTER: wx_plain_wrapper,
    SIGNAL_TABCHANGED: wx_tabchanged_wrapper,
    SIGNAL_CLOSING: wx_plain_wrapper,
    SIGNAL_HIDDEN: wx_plain_wrapper }

class _PWxCommunicator(object):
    """
    A mixin class to abstract notification functionality in wxWidgets.
    """
    
    def setup_notify(self, signal, target, wrap=True):
        if signal in _wxeventmap:
            event = _wxeventmap[signal]
            if wrap and (signal in _wxwrappermap):
                handler = _wxwrappermap[signal](self, target)
            else:
                handler = target
            
            # Do the following instead of self.Bind(event, handler) so
            # that multiple handlers can receive a single event
            eventManager.Register(handler, event, self)
    
    def do_notify(self, signal, *args):
        if signal in _wxcustommap:
            event = _wxcustommap[signal]()
        elif signal in _wxeventmap:
            event = wx.Event()
            event.SetEventType(_wxeventmap[signal])
            if hasattr(self, 'id'):
                event.SetEventID(self.id)
            elif hasattr(self, 'GetId'):
                event.SetEventID(self.GetId())
        if event is not None:
            event.SetEventObject(self)
            self.AddPendingEvent(event)

class _PWxWidgetBase(object):
    """ Mixin class to provide basic wx widget methods. """
    
    def update(self):
        self.Refresh()
    
    def preferred_width(self):
        return self.GetSizeTuple()[0]
    
    def preferred_height(self):
        return self.GetSizeTuple()[1]
    
    def set_width(self, width):
        height = self.GetSizeTuple()[1]
        self.SetSizeWH(width, height)
        self.SetMinSize((width, height))
    
    def set_height(self, height):
        width = self.GetSizeTuple()[0]
        self.SetSizeWH(width, height)
        self.SetMinSize((width, height))
    
    def set_position(self, left, top):
        if not (None in (left, top)):
            self.SetPosition(wx.Point(left, top))
    
    def set_foreground_color(self, color):
        self.SetForegroundColour(color)
    
    def get_font_name(self):
        font = self.GetFont()
        return font.GetFaceName()
    
    def get_font_size(self):
        font = self.GetFont()
        return font.GetPointSize()
    
    def set_font(self, font_name, font_size=None):
        if font_size is None:
            font_size = default_font_size
        font_family = wx.FONTFAMILY_DEFAULT
        for family, names in _wxfontfamilies.iteritems():
            if font_name in names:
                font_family = family
                break
        font_style = wx.FONTSTYLE_NORMAL
        font_weight = wx.FONTWEIGHT_NORMAL
        font = wx.Font(font_size, font_family, font_style, font_weight)
        font.SetFaceName(font_name)
        self.SetFont(font)
    
    def _get_enabled(self):
        return self.IsEnabled()
    
    def _set_enabled(self, value):
        self.Enable(value)
    
    enabled = property(_get_enabled, _set_enabled)
    
    def set_focus(self):
        self.SetFocus()

class _PWxWidget(_PWxCommunicator, _PWxWidgetBase):
    """ Mixin class for wx widgets that can send/receive signals. """
    pass

class _PWxClientWidget(_PWxWidget):
    """ Mixin class for wx client widgets (i.e., can be used as client of main window). """
    pass
