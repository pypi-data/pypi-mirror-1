#!/usr/bin/env python
"""
Module QTCOMMON -- Python Qt Common Objects
Sub-Package GUI.TOOLKITS.QT of Package PLIB -- Python GUI Toolkits
Copyright (C) 2008 by Peter A. Donis

This module contains common Qt GUI objects for use by the other
Qt modules.
"""

import qt

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
    SIGNAL_TOGGLED: "clicked()",
    SIGNAL_LISTVIEWCHANGED: "currentChanged()",
    SIGNAL_TABLECHANGED: "valueChanged(int, int)",
    SIGNAL_TEXTCHANGED: "textChanged()",
    SIGNAL_ENTER: "returnPressed()",
    SIGNAL_BEFOREQUIT: "aboutToQuit()" }

_qteventmap = {
    SIGNAL_QUERYCLOSE: "closeEvent",
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

class _PQtWidget(_PQtCommunicator):
    """ Mixin class to provide some 'standard' Qt widget methods. """
    
    def set_geometry(self, left, top, width, height):
        self.setGeometry(left, top, width, height)
    
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
