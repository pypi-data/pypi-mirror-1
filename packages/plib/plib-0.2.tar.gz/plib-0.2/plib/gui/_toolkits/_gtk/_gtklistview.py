#!/usr/bin/env python
"""
Module GTKLISTVIEW -- Python GTK Tree/List View Objects
Sub-Package GUI.TOOLKITS.GTK of Package PLIB -- Python GUI Toolkits
Copyright (C) 2008 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the GTK GUI objects for the tree/list view widgets.
"""

import pygtk
pygtk.require('2.0')
import gtk
import gobject

from plib.gui.defs import *
from plib.gui._widgets import listview

from _gtkcommon import _PGtkWidget, _gtkalignmap, _gtksignals

class _PGtkListViewMixin(object):
    
    def _newitem(self, index, value):
        if index == len(self):
            before = None
        else:
            before = self._items[index]
        return self.itemclass(self, index, value, before)

class PGtkListViewItem(_PGtkListViewMixin, listview.PListViewItemBase):
    
    def __init__(self, parent, index, data=None, before=None):
        self._b = before # ugly hack since we have to postpone creating the gtk tree iter until _set_col below
        listview.PListViewItemBase.__init__(self, parent, index, data)
    
    def _helperdel(self, index, item):
        self.listview._model.remove(item._iter)
    
    def _get_col(self, col):
        return self.listview._model.get_value(self._iter, col)
    
    def _set_col(self, col, value):
        if (col == 0) and not hasattr(self, '_iter'):
            if self._b is not None:
                self._iter = self.listview._model.insert_before(self._parent._iter, self._b._iter)
            else:
                self._iter = self.listview._model.append(self._parent._iter)
            # this trick will allow PGtkListView.current_item to work
            self.listview._model.set_value(self._iter, self.listview._objcol, self)
            # ugly hack to clear up instance namespace
            del self._b
        self.listview._model.set_value(self._iter, col, value)
    
    def expand(self):
        self.listview.expand_to_path(self.listview._model.get_path(self._iter))

class PGtkListViewLabels(listview.PListViewLabelsBase):
    
    def __init__(self, parent, labels):
        self._columns = []
        listview.PListViewLabelsBase.__init__(self, parent, labels)
    
    def _set_label(self, index, label):
        if index == len(self._columns):
            column = gtk.TreeViewColumn(label, gtk.CellRendererText(), text=index)
            column.set_expand(True)
            column.set_sizing(gtk.TREE_VIEW_COLUMN_FIXED)
            self.listview.append_column(column)
            self._columns.append(column)
        else:
            self._columns[index].set_title(label)
    
    def _set_width(self, index, width):
        if width < 1:
            width = self.defaultwidth
        #self._columns[index].set_min_width(width)
        self._columns[index].set_fixed_width(width)
    
    def _set_align(self, index, align):
        self._columns[index].set_alignment(_gtkalignmap[align])
    
    def _set_readonly(self, index, readonly):
        pass

class PGtkListView(gtk.TreeView, _PGtkWidget, _PGtkListViewMixin, listview.PListViewBase):
    
    itemclass = PGtkListViewItem
    labelsclass = PGtkListViewLabels
    
    # Define list view changed signal using 'automagic' class field
    __gsignals__ = { _gtksignals[SIGNAL_LISTVIEWCHANGED]:
        (gobject.SIGNAL_RUN_LAST,
        gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT,)) }
    
    def __init__(self, parent, labels=None, data=None, target=None):
        args = tuple([gobject.TYPE_STRING for label in labels] + [gobject.TYPE_PYOBJECT])
        self._model = gtk.TreeStore(*args)
        self._iter = None # easier logic for adding top level items
        self._objcol = len(labels) # column that each item's Python self object reference will be stored in
        gtk.TreeView.__init__(self, self._model)
        _PGtkWidget.__init__(self, parent, ALIGN_JUST)
        listview.PListViewBase.__init__(self, parent, labels, data, target)
        
        # The list view changed signal doesn't contain the current item, so gateway it
        self.connect("cursor_changed", self.cursor_changed)
    
    def cursor_changed(self, obj):
        """ The list view selection cursor was changed. """
        self.do_notify(SIGNAL_LISTVIEWCHANGED, self.current_item())
    
    def __iter__(self):
        """ Need to override gtk.TreeView's iter method. """
        return listview.PListViewBase.__iter__(self)
    
    def __len__(self):
        """ Need to override gtk.TreeView's len method. """
        return listview.PListViewBase.__len__(self)
    
    def _helperdel(self, index, item):
        self._model.remove(item._iter)
    
    def colcount(self):
        return self._model.get_n_columns()
    
    def current_item(self):
        model, iter = self.get_selection().get_selected()
        assert model == self._model # if this throws an exception then everything's fubar
        # the Python self pointer for the item was stored in the iter in column self._objcol above
        return model.get_value(iter, self._objcol)
    
    def set_current_item(self, item):
        self.get_selection().select_iter(item._iter)
