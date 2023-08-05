#!/usr/bin/env python
"""
Module KDELISTVIEW -- Python KDE Tree/List View Objects
Sub-Package GUI.TOOLKITS.KDE of Package PLIB -- Python GUI Toolkits
Copyright (C) 2008 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the KDE GUI objects for the tree/list view widgets.
"""

import kdeui

from plib.gui._widgets import listview

from _kdecommon import _PKDECommunicator, _kdealignmap

class _PKDEListViewMixin(object):
    """
    Mixin class to handle KDE-specific (read: KDE-weird) behavior of list views
    and list view items.
    """
    
    def _newitem(self, index, value):
        # First have to decide whether we need to insert after another item
        if index == 0:
            after = None
        else:
            after = self._items[index - 1]
        
        # Now we can instantiate the new item
        return self.itemclass(self, index, value, after)
    
    def _helperdel(self, index, item):
        # Remove item from the parent list view or list view item
        self.takeItem(item)

class PKDEListViewItem(kdeui.KListViewItem, _PKDEListViewMixin,
    listview.PListViewItemBase, _PKDECommunicator):
    
    def __init__(self, parent, index, data=None, after=None):
        if after is not None:
            kdeui.KListViewItem.__init__(self, parent, after)
        else:
            kdeui.KListViewItem.__init__(self, parent)
        listview.PListViewItemBase.__init__(self, parent, index, data)
    
    def _get_col(self, col):
        return str(self.text(col))
    
    def _set_col(self, col, value):
        self.setText(col, str(value))
    
    def expand(self):
        self.setOpen(True)

class PKDEListViewLabels(listview.PListViewLabelsBase):
    
    def _set_label(self, index, label):
        if self.listview.columns() == index:
            self.listview.addColumn(str(label))
        else:
            self.listview.setColumnText(index, str(label))
    
    def _set_width(self, index, width):
        self.listview.setColumnWidth(index, width)
    
    def _set_align(self, index, align):
        self.listview.setColumnAlignment(index, _kdealignmap[align])
    
    def _set_readonly(self, index, readonly):
        pass

class PKDEListView(kdeui.KListView, _PKDEListViewMixin,
    listview.PListViewBase, _PKDECommunicator):
    
    itemclass = PKDEListViewItem
    labelsclass = PKDEListViewLabels
    
    def __init__(self, parent, labels=None, data=None, target=None):
        kdeui.KListView.__init__(self, parent)
        self.setSorting(-1)
        self.setRootIsDecorated(True)
        listview.PListViewBase.__init__(self, parent, labels, data, target)
    
    def colcount(self):
        return self.columns()
    
    def current_item(self):
        return self.currentItem()
    
    def set_current_item(self, item):
        self.setCurrentItem(item)
