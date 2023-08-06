#!/usr/bin/env python
"""
Module KDE4LISTVIEW -- Python KDE Tree/List View Objects
Sub-Package GUI.TOOLKITS.KDE of Package PLIB -- Python GUI Toolkits
Copyright (C) 2008-2009 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the KDE 4 GUI objects for the tree/list view widgets.
"""

# The KDE 4 "list view" is less flexible, so just use the Qt 4 widget
from PyQt4 import Qt as qt

from plib.gui._widgets import listview

from _kde4common import _PKDEWidget, _PKDEClientWidget, _PKDECommunicator, _kdealignmap

class PKDEListViewItem(qt.QTreeWidgetItem, listview.PListViewItemBase, _PKDECommunicator):
    
    def __init__(self, parent, index, data=None):
        qt.QTreeWidgetItem.__init__(self, parent)
        parent._insert(self, index)
        listview.PListViewItemBase.__init__(self, parent, index, data)
    
    def _insert(self, item, index):
        if index == len(self):
            self.addChild(item)
        else:
            self.insertChild(index, item)
    
    def _helperdel(self, index, item):
        self.takeChild(index)
    
    def _get_col(self, col):
        return str(self.text(col))
    
    def _set_col(self, col, value):
        self.setText(col, str(value))
    
    def expand(self):
        self.setExpanded(True)

class PKDEListViewLabels(listview.PListViewLabelsBase):
    
    label_list = None
    labels_initialized = False
    
    def _update(self, data):
        # Hack to get around weirdness in Qt 4 table widget API
        self.label_list = [str(value) for value in data]
        listview.PListViewLabelsBase._update(self, data)
    
    def _set_label(self, index, label):
        if self.label_list is not None:
            # First time setting labels, do it this way
            self.listview.setHeaderLabels(self.label_list)
            self.label_list = None
        if self.labels_initialized:
            # This allows labels to be changed after the initial setup
            item = self.listview.headerItem()
            item.setText(index, label)
        elif index == (len(self) - 1):
            # End of initial run
            self.labels_initialized = True
    
    def _set_width(self, index, width):
        if width > 0:
            # FIXME: the last column doesn't respect fixed sizing
            self.listview.setColumnWidth(index, width)
        # FIXME: implement auto-sizing of column if width is -1
    
    def _set_align(self, index, align):
        item = self.listview.headerItem()
        item.setTextAlignment(index, _kdealignmap[align])
        # FIXME: need to align the whole column, not just the header
    
    def _set_readonly(self, index, readonly):
        #self.table.setColumnReadOnly(index, readonly)
        pass

class _PKDEListViewBase(qt.QTreeWidget):
    
    widget_class = qt.QTreeWidget
    
    itemclass = PKDEListViewItem
    labelsclass = PKDEListViewLabels
    
    def __init__(self, parent):
        qt.QTreeWidget.__init__(self, parent)
        self.setSortingEnabled(False)
        self.setRootIsDecorated(True)
    
    def _insert(self, item, index):
        if index == len(self):
            self.addTopLevelItem(item)
        else:
            self.insertTopLevelItem(index, item)
    
    # FIXME: Qt 4 doesn't set the header font when the listview font is set.
    # Would like to hack a fix here, but the below doesn't scale the header!@#$%^&*
    #def set_font(self, font_name, font_size=None):
    #    if font_size is None:
    #        font_size = default_font_size
    #    font = qt.QFont(font_name, font_size)
    #    self.setFont(font)
    #    for col in range(len(self.labels)):
    #        item = self.labels._headeritem
    #        label = item.text(col)
    #        item.setFont(col, font)
    #        item.setText(col, label)
    
    def _helperdel(self, index, item):
        self.takeTopLevelItem(index)
    
    def colcount(self):
        return self.columnCount()
    
    def current_item(self):
        return self.currentItem()
    
    def set_current_item(self, item):
        self.setCurrentItem(item)

class PKDEListView(_PKDEListViewBase, _PKDEClientWidget, listview.PListViewBase):
    
    def __init__(self, parent, labels=None, data=None, target=None):
        _PKDEListViewBase.__init__(self, parent)
        listview.PListViewBase.__init__(self, parent, labels, data, target)

class PKDEListBox(_PKDEListViewBase, _PKDEWidget, listview.PListBoxBase):
    
    def __init__(self, parent, labels=None, data=None, target=None, geometry=None):
        _PKDEListViewBase.__init__(self, parent)
        listview.PListBoxBase.__init__(self, parent, labels, data, target, geometry)
