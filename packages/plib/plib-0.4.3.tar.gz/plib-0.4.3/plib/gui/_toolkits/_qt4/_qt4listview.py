#!/usr/bin/env python
"""
Module QT4LISTVIEW -- Python Qt 4 Tree/List View Objects
Sub-Package GUI.TOOLKITS.QT4 of Package PLIB -- Python GUI Toolkits
Copyright (C) 2008 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the Qt 4 GUI objects for the tree/list view widgets.
"""

from PyQt4 import Qt as qt

from plib.gui._widgets import listview

from _qt4common import _PQtClientWidget, _PQtCommunicator, _qtalignmap

class _PQtListViewMixin(object):
    """
    Mixin class to handle Qt-specific (read: Qt-weird) behavior of list views
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

class PQtListViewItem(qt.QTreeWidgetItem, _PQtListViewMixin,
    listview.PListViewItemBase, _PQtCommunicator):
    
    def __init__(self, parent, index, data=None, after=None):
        if after is not None:
            qt.QTreeWidgetItem.__init__(self, parent, after)
        else:
            qt.QTreeWidgetItem.__init__(self, parent)
        listview.PListViewItemBase.__init__(self, parent, index, data)
    
    def _helperdel(self, index, item):
        self.takeChild(index)
    
    def _get_col(self, col):
        return str(self.text(col))
    
    def _set_col(self, col, value):
        self.setText(col, str(value))
    
    def expand(self):
        self.setExpanded(True)

class PQtListViewLabels(listview.PListViewLabelsBase):
    
    def __init__(self, helper, labels=None):
        self._headeritem = qt.QTreeWidgetItem()
        listview.PListViewLabelsBase.__init__(self, helper, labels)
        self.listview.setColumnCount(len(labels))
        self.listview.setHeaderItem(self._headeritem)
    
    def _set_label(self, index, label):
        self._headeritem.setText(index, str(label))
    
    def _set_width(self, index, width):
        height = self._headeritem.sizeHint(index).height()
        self._headeritem.setSizeHint(index, qt.QSize(width, height))
    
    def _set_align(self, index, align):
        self._headeritem.setTextAlignment(index, _qtalignmap[align])
    
    def _set_readonly(self, index, readonly):
        pass

class PQtListView(qt.QTreeWidget, _PQtListViewMixin, _PQtClientWidget,
    listview.PListViewBase):
    
    itemclass = PQtListViewItem
    labelsclass = PQtListViewLabels
    
    def __init__(self, parent, labels=None, data=None, target=None):
        qt.QTreeWidget.__init__(self, parent)
        self.setSortingEnabled(False)
        self.setRootIsDecorated(True)
        listview.PListViewBase.__init__(self, parent, labels, data, target)
    
    def _helperdel(self, index, item):
        self.takeTopLevelItem(index)
    
    def colcount(self):
        return self.columnCount()
    
    def current_item(self):
        return self.currentItem()
    
    def set_current_item(self, item):
        self.setCurrentItem(item)
