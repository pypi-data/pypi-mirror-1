#!/usr/bin/env python
"""
Module QTCOMMON -- Python Qt Common Objects
Sub-Package GUI.TOOLKITS.QT of Package PLIB -- Python GUI Toolkits
Copyright (C) 2008-2009 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains common Qt GUI objects for use by the other
Qt modules.
"""

import qt

from plib.gui.defs import *

_qtalignmap = {
    ALIGN_LEFT: qt.Qt.AlignLeft,
    ALIGN_CENTER: qt.Qt.AlignCenter,
    ALIGN_RIGHT: qt.Qt.AlignRight }

_qtcolormap = dict((color, qt.QColor(color.lower()))
    for color in COLORNAMES)

_qtmessagefuncs = {
    MBOX_INFO: qt.QMessageBox.information,
    MBOX_WARN: qt.QMessageBox.warning,
    MBOX_ERROR: qt.QMessageBox.critical,
    MBOX_QUERY: qt.QMessageBox.question }

_qtsignalmap = {
    SIGNAL_ACTIVATED: "activated()",
    SIGNAL_CLICKED: "clicked()",
    SIGNAL_TOGGLED: "clicked()",
    SIGNAL_SELECTED: "activated(int)",
    SIGNAL_LISTVIEWCHANGED: "currentChanged(QListViewItem*)",
    SIGNAL_TABLECHANGED: "valueChanged(int, int)",
    SIGNAL_TEXTCHANGED: "textChanged()",
    SIGNAL_EDITCHANGED: "textChanged(const QString&)",
    SIGNAL_ENTER: "returnPressed()",
    SIGNAL_TABCHANGED: "currentChanged(QWidget*)",
    SIGNAL_NOTIFIER: "activated(int)",
    SIGNAL_BEFOREQUIT: "aboutToQuit()" }

_qteventmap = {
    SIGNAL_FOCUS_IN: "focusInEvent",
    SIGNAL_FOCUS_OUT: "focusOutEvent",
    SIGNAL_CLOSING: "closeEvent",
    SIGNAL_HIDDEN: "hideEvent" }

def _qtmap(signal):
    if signal in _qtsignalmap:
        return qt.SIGNAL(_qtsignalmap[signal])
    elif signal in _qteventmap:
        return qt.PYSIGNAL(_qteventmap[signal])
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
    
    def set_width(self, width):
        self.resize(width, self.height())
    
    def set_height(self, height):
        self.resize(self.width(), height)
    
    def set_position(self, left, top):
        if not (None in (left, top)):
            self.move(left, top)
    
    def set_foreground_color(self, color):
        self.setPaletteForegroundColor(_qtcolormap[color])
    
    def get_font_name(self):
        return self.font().family()
    
    def get_font_size(self):
        return self.font().pointSize()
    
    def set_font(self, font_name, font_size=None):
        if font_size is None:
            font_size = default_font_size
        self.setFont(qt.QFont(font_name, font_size))
    
    def _get_enabled(self):
        return self.isEnabled()
    
    def _set_enabled(self, value):
        self.setEnabled(value)
    
    enabled = property(_get_enabled, _set_enabled)
    
    def set_focus(self):
        self.setFocus()

class _PQtWidget(_PQtCommunicator, _PQtWidgetBase):
    """ Mixin class for Qt widgets that can send/receive signals. """
    
    widget_class = None
    
    def focusInEvent(self, event):
        self.widget_class.focusInEvent(self, event)
        self._emit_event(SIGNAL_FOCUS_IN)
    
    def focusOutEvent(self, event):
        self.widget_class.focusOutEvent(self, event)
        self._emit_event(SIGNAL_FOCUS_OUT)

class _PQtClientWidget(_PQtWidget):
    """ Mixin class for Qt client widgets (i.e., can be used as client of main window). """
    pass
