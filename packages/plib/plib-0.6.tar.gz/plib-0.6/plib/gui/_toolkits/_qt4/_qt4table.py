#!/usr/bin/env python
"""
Module QT4TABLE -- Python Qt 4 Table Objects
Sub-Package GUI.TOOLKITS.QT4 of Package PLIB -- Python GUI Toolkits
Copyright (C) 2008 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the Qt 4 GUI objects for the table widgets.
"""

from PyQt4 import Qt as qt

from plib.gui._widgets import table

from _qt4common import _PQtClientWidget, _qtalignmap, _qtcolormap

class PQtTableLabels(table.PTableLabelsBase):
    
    #def __init__(self, helper, labels=None):
        #self.table.setColumnCount(len(labels))
        #table.PTableLabelsBase.__init__(self, helper, labels)
    
    def _set_label(self, index, label):
        item = qt.QTableWidgetItem(label)
        self.table.setHorizontalHeaderItem(index, item)
    
    def _set_width(self, index, width):
        item = self.table.horizontalHeaderItem(index)
        height = item.sizeHint().height()
        item.setSizeHint(qt.QSize(width, height))
    
    def _set_align(self, index, align):
        self.table.horizontalHeaderItem(index).setTextAlignment(_qtalignmap[align])
    
    def _set_readonly(self, index, readonly):
        pass
        #self.table.setColumnReadOnly(index, readonly)

class PQtTable(qt.QTableWidget, _PQtClientWidget, table.PTableBase):
    
    labelsclass = PQtTableLabels
    
    def __init__(self, parent, labels=None, data=None, target=None):
        qt.QTableWidget.__init__(self, parent)
        self.setSortingEnabled(False)
        
        # These will be needed to hack customized colors below
        #self.textcolors = {}
        #self.cellcolors = {}
        #self._painted = False
        
        # This will initialize data (if any)
        table.PTableBase.__init__(self, parent, labels, data, target)
    
    def _get_item(self, row, col):
        result = self.item(row, col)
        if not isinstance(result, qt.QTableWidgetItem):
            result = qt.QTableWidgetItem()
            self.setItem(row, col, result)
        return result
    
    def _get_cell(self, row, col):
        # Need str conversion here since widgets return QStrings
        return str(self._get_item(row, col).text())
    
    def _set_cell(self, row, col, value):
        self._get_item(row, col).setText(str(value))
    
    def rowcount(self):
        return self.rowCount()
    
    def colcount(self):
        return self.columnCount()
    
    def set_colcount(self, count):
        self.setColumnCount(count)
    
    def current_row(self):
        return self.currentRow()
    
    def current_col(self):
        return self.currentColumn()
    
    def _insert_row(self, index):
        rows = self.rowcount()
        cols = self.colcount()
        self.setRowCount(rows + 1)
        for i in range(index, rows):
            for j in range(cols):
                value = self._get_cell(i, j)
                self._set_cell(i + 1, j, value)
                self._set_cell(i, j, "")
    
    def _remove_row(self, index):
        rows = self.rowcount()
        cols = self.colcount()
        for i in range(index + 1, rows):
            for j in range(cols):
                value = self._get_cell(i, j)
                self._set_cell(i - 1, j, value)
                self._set_cell(i, j, "")
        self.setRowCount(rows - 1)
    
    def set_min_size(self, width, height):
        self.setMinimumSize(width, height)
    
    def topmargin(self):
        return 0 #self.topMargin()
    
    def leftmargin(self):
        return 0 #self.leftMargin()
    
    def rowheight(self, row):
        return self.rowHeight(row)
    
    def colwidth(self, col):
        return self.columnWidth(col)
    
    #def default_fgcolor(self):
    #    return None
    
    #def default_bkcolor(self):
    #    return None
    
    #def _set_color(self, mapping, row, col, color):
    #    if color is None:
    #        if (row, col) in mapping:
    #            del mapping[(row, col)]
    #    else:
    #        mapping[(row, col)] = _qtcolormap[color]
    
    def _set_color(self, brush, color):
        brush.setColor(_qtcolormap[color])
    
    def set_text_fgcolor(self, row, col, color):
        item = self._get_item(row, col)
        brush = item.foreground()
        self._set_color(brush, color)
        #self._set_color(self.textcolors, row, col, color)
    
    def set_cell_bkcolor(self, row, col, color):
        item = self._get_item(row, col)
        brush = item.background()
        self._set_color(brush, color)
        #self._set_color(self.cellcolors, row, col, color)
    
    #def force_repaint(self):
    #    if self._painted:
    #        self.invalidate()
    #        self.erase()
    #        self.update()
    
    #def paintCell(self, painter, row, col, rect, selected, colorgroup=None):
    #    """
    #    Overridden paintCell method to allow customized text and background colors.
    #    """
        
        #if not self._painted:
        #    self._painted = True
        
        # FIXME: wtf isn't this already built into Qt???
    #    if colorgroup is not None:
    #        if (row, col) in self.textcolors:
    #            colorgroup.setColor(qt.QColorGroup.Text, self.textcolors[(row, col)])
    #        if (row, col) in self.cellcolors:
    #            colorgroup.setColor(qt.QColorGroup.Base, self.cellcolors[(row, col)])
    #        qt.QTableWidget.paintCell(self, painter, row, col, rect, selected, colorgroup)
    #    else:
    #        # FIXME: while we're venting, wtf is this block necessary? (i.e., why can't
    #        # we just make the above call with colorgroup set to None?)
    #        qt.QTableWidget.paintCell(self, painter, row, col, rect, selected)
