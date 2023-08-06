#!/usr/bin/env python
"""
Module WXLISTVIEW -- Python wxWidgets Tree/List View Objects
Sub-Package GUI.TOOLKITS.WX of Package PLIB -- Python GUI Toolkits
Copyright (C) 2008 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the wxWidgets GUI objects for the tree/list view widgets.
"""

import wx
import wx.gizmos as gizmos

from plib.gui.defs import *
from plib.gui._widgets import listview

from _wxcommon import _PWxClientWidget

class _PWxListViewMixin(object):
    
    def _newitem(self, index, value):
        if index == len(self):
            before = None
        else:
            before = self._items[index]
        return self.itemclass(self, index, value, before)

class PWxListViewItem(_PWxListViewMixin, listview.PListViewItemBase):
    
    def __init__(self, parent, index, data=None, before=None):
        self._b = before # ugly hack since we have to postpone creating the wx tree item until _set_col below
        listview.PListViewItemBase.__init__(self, parent, index, data)
    
    def _helperdel(self, index, item):
        self.listview.Delete(item._id)
    
    def _get_col(self, col):
        return self.listview.GetItemText(self._id, col)
    
    def _set_col(self, col, value):
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
        self._templabel = None
    
    def _set_label(self, index, label):
        if (index == self.listview.colcount()):
            self.listview.AddColumn(label, self.defaultwidth)
        else:
            self.listview.SetColumnText(index, label)
    
    def _set_width(self, index, width):
        #FIXME: why does this crash if there are no child items yet?
        #self.listview.SetColumnWidth(index, width)
        pass
    
    def _set_align(self, index, align):
        pass
    
    def _set_readonly(self, index, readonly):
        pass

class PWxListView(gizmos.TreeListCtrl, _PWxListViewMixin, _PWxClientWidget,
    listview.PListViewBase):
    
    itemclass = PWxListViewItem
    labelsclass = PWxListViewLabels
    
    def __init__(self, parent, labels=None, data=None, target=None):
        gizmos.TreeListCtrl.__init__(self, parent,
            style=wx.TR_HAS_BUTTONS | wx.TR_HIDE_ROOT | wx.TR_FULL_ROW_HIGHLIGHT)
        self._align = ALIGN_JUST # used by PWxPanel to determine placement
        self._expand = True
        listview.PListViewBase.__init__(self, parent, labels, data, target)
        if labels is not None:
            self.Expand(self._id)
    
    def _helperdel(self, index, item):
        self.Delete(item._id)
    
    def colcount(self):
        return self.GetColumnCount()
    
    def current_item(self):
        # the list view item stored its self pointer in the wx tree item's PyData above
        return self.GetItemPyData(self.GetSelection())
    
    def set_current_item(self, item):
        self.SelectItem(item._id)
