#!/usr/bin/env python
"""
Module WXLISTVIEW -- Python wxWidgets Tree/List View Objects
Sub-Package GUI.TOOLKITS.WX of Package PLIB -- Python GUI Toolkits
Copyright (C) 2008-2009 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the wxWidgets GUI objects for the tree/list view widgets.
"""

import wx
import wx.gizmos as gizmos

from plib.gui.defs import *
from plib.gui._widgets import listview

from _wxcommon import _PWxClientWidget, _PWxWidget

class PWxListViewItem(listview.PListViewItemBase):
    
    def __init__(self, parent, index, data=None):
        if index == len(parent):
            before = None
        else:
            before = parent._items[index]
        self._b = before # ugly hack since we have to postpone creating the wx tree item until _set_col below
        listview.PListViewItemBase.__init__(self, parent, index, data)
    
    def _helperdel(self, index, item):
        self.listview.Delete(item._id)
    
    def _get_col(self, col):
        return self.listview.GetItemText(self._id, col)
    
    def _set_col(self, col, value):
        value = str(value) # just in case
        if (col == 0) and not hasattr(self, '_id'):
            if self._b is not None:
                self._id = self.listview.InsertItem(self._parent._id, self._b._id, value)
            else:
                self._id = self.listview.AppendItem(self._parent._id, value)
            # this trick is to allow PWxListView.current_item to work
            self.listview.SetItemPyData(self._id, self)
            # ugly hack to clear up the instance namespace
            del self._b
        else:
            self.listview.SetItemText(self._id, value, col)
    
    def expand(self):
        self.listview.Expand(self._id)

class PWxListViewLabels(listview.PListViewLabelsBase):
    
    def __init__(self, helper, labels=None):
        listview.PListViewLabelsBase.__init__(self, helper, labels)
        self.listview._id = self.listview.AddRoot("root")
        #self._templabel = None
    
    def _set_label(self, index, label):
        if (index == self.listview.colcount()):
            self.listview.AddColumn(label)
        else:
            self.listview.SetColumnText(index, label)
    
    def _set_width(self, index, width):
        if width > 0:
            # FIXME: the last column doesn't respect fixed sizing
            self.listview.SetColumnWidth(index, width)
        # FIXME: Implement auto-sizing of columns if width is -1
    
    def _set_align(self, index, align):
        pass
    
    def _set_readonly(self, index, readonly):
        pass

class _PWxListViewBase(gizmos.TreeListCtrl):
    
    itemclass = PWxListViewItem
    labelsclass = PWxListViewLabels
    
    def __init__(self, parent):
        gizmos.TreeListCtrl.__init__(self, parent,
            style=wx.TR_HAS_BUTTONS | wx.TR_HIDE_ROOT | wx.TR_FULL_ROW_HIGHLIGHT)
        self._align = ALIGN_JUST # used by PWxPanel to determine placement
        self._expand = True
    
    def _helperdel(self, index, item):
        self.Delete(item._id)
    
    def colcount(self):
        return self.GetColumnCount()
    
    def current_item(self):
        # the list view item stored its self pointer in the wx tree item's PyData above
        return self.GetItemPyData(self.GetSelection())
    
    def set_current_item(self, item):
        self.SelectItem(item._id)

class PWxListView(_PWxListViewBase, _PWxClientWidget, listview.PListViewBase):
    
    def __init__(self, parent, labels=None, data=None, target=None):
        _PWxListViewBase.__init__(self, parent)
        listview.PListViewBase.__init__(self, parent, labels, data, target)
        if labels is not None:
            self.Expand(self._id)

class PWxListBox(_PWxListViewBase, _PWxWidget, listview.PListBoxBase):
    
    def __init__(self, parent, labels=None, data=None, target=None, geometry=None):
        _PWxListViewBase.__init__(self, parent)
        listview.PListBoxBase.__init__(self, parent, labels, data, target, geometry)
        if labels is not None:
            self.Expand(self._id)
