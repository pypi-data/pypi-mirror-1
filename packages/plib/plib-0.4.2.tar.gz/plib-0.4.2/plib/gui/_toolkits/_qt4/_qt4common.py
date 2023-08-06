#!/usr/bin/env python
"""
Module QTCOMMON4 -- Python Qt 4 Common Objects
Sub-Package GUI.TOOLKITS.QT4 of Package PLIB -- Python GUI Toolkits
Copyright (C) 2008 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains common Qt 4 GUI objects for use by the other
Qt modules.
"""

from PyQt4 import Qt as qt

from plib.gui.defs import *

_qtalignmap = {
    ALIGN_LEFT: qt.Qt.AlignLeft,
    ALIGN_CENTER: qt.Qt.AlignCenter,
    ALIGN_RIGHT: qt.Qt.AlignRight }

_qtcolormap = {
    COLOR_BLACK: qt.QColor('black'),
    COLOR_RED: qt.QColor('red'),
    COLOR_BLUE: qt.QColor('blue'),
    COLOR_GREEN: qt.QColor('green'),
    COLOR_YELLOW: qt.QColor('yellow'),
    COLOR_WHITE: qt.QColor('white') }

_qtmessagefuncs = {
    MBOX_INFO: qt.QMessageBox.information,
    MBOX_WARN: qt.QMessageBox.warning,
    MBOX_ERROR: qt.QMessageBox.critical,
    MBOX_QUERY: qt.QMessageBox.question }

_qtsignalmap = {
    SIGNAL_ACTIVATED: "activated()",
    SIGNAL_CLICKED: "clicked()",
    SIGNAL_TOGGLED: "clicked()", # toggled(bool)?
    SIGNAL_SELECTED: "activated(int)",
    SIGNAL_LISTVIEWCHANGED: "currentChanged(QTreeWidgetItem*, QTreeWidgetItem*)",
    SIGNAL_TABLECHANGED: "cellChanged(int, int)",
    SIGNAL_TEXTCHANGED: "textChanged()", # textEdited()?
    SIGNAL_EDITCHANGED: "textChanged(const QString&)", # textEdited(const QString&)?
    SIGNAL_ENTER: "returnPressed()",
    SIGNAL_TABCHANGED: "currentChanged(int)",
    SIGNAL_BEFOREQUIT: "aboutToQuit()" }

_qteventmap = {
    SIGNAL_CLOSING: "closeEvent",
    SIGNAL_HIDDEN: "hideEvent" }

def _qtmap(signal):
    if signal in _qtsignalmap:
        return qt.SIGNAL(_qtsignalmap[signal])
    elif signal in _qteventmap:
        return qt.SIGNAL(_qteventmap[signal])
    else:
        return None

# NOTE: we don't need to define 'wrapper' methods here like we do under GTK and
# wxWidgets because Qt silently discards any extra parameters that are not
# accepted by a signal handler. (BTW, this is good because wrappers don't seem
# to work like they should in Qt -- see PEDIT.PY, PEditor._setup_signals.)

class _PQtCommunicator(object):
    """
    A mixin class to abstract signal/slot functionality in Qt.
    """
    
    def setup_notify(self, signal, target):
        if signal in _qteventmap:
            # hack to make Qt event methods look like signals
            if not hasattr(self, _qteventmap[signal]):
                return
            self.enabled_events[signal] = True
        qt.QObject.connect(self, _qtmap(signal), target)
    
    def do_notify(self, signal, *args):
        sig = _qtmap(signal)
        if sig is not None:
            self.emit(sig, args)
    
    # need the following for widget events that have to have an overridden
    # handler defined in the class (can't "substitute on the fly") so that
    # they can work like signals
    
    enabled_events = {}
    
    def _emit_event(self, signal):
        if signal in self.enabled_events:
            self.do_notify(signal)

class _PQtWidgetBase(object):
    """ Mixin class to provide minimal Qt widget methods. """
    
    def preferred_width(self):
        return self.sizeHint().width()
    
    def preferred_height(self):
        return self.sizeHint().height()

class _PQtClientWidget(_PQtCommunicator, _PQtWidgetBase):
    """ Mixin class for Qt client widgets. """
    
    def get_font_name(self):
        return self.font().family()
    
    def get_font_size(self):
        return self.font().pointSize()
    
    def set_font(self, font_name, font_size=None):
        if font_size is None:
            font_size = default_font_size
        self.setFont(qt.QFont(font_name, font_size))

class _PQtWidget(_PQtClientWidget):
    """ Mixin class to provide some more 'standard' Qt widget methods. """
    
    def set_width(self, width):
        self.resize(width, self.height())
    
    def set_height(self, height):
        self.resize(self.width(), height)
    
    def set_position(self, left, top):
        if not (None in (left, top)):
            self.move(left, top)
    
    def _get_enabled(self):
        return self.isEnabled()
    
    def _set_enabled(self, value):
        self.setEnabled(value)
    
    enabled = property(_get_enabled, _set_enabled)
    
    def set_focus(self):
        self.setFocus()
