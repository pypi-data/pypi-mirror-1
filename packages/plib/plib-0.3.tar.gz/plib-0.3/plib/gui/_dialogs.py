#!/usr/bin/env python
"""
Module DIALOGS -- Dialog Classes for GUI
Sub-Package GUI of Package PLIB -- Python GUI Framework
Copyright (C) 2008 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

Defines dialogs for use with PLIB.GUI applications. The
PDialogBase class implements the core functionality to
make it easy to integrate a dialog with a PLIB.GUI
application. The following specific dialogs are also
included:

PPrefsDialog -- automatically constructs a dialog to
allow editing of the preferences stored in a PIniFile.
"""

from plib.gui import main as gui
from plib.gui.defs import *
from plib.gui.specs import *

from plib.ini.defs import *

# Now we can import the rest of the stuff

class PDialogBase(gui.PTopWindow):
    """
    Base class for dialogs; assumes that self.defs
    exists and contains a list of control definitions
    for use by a PAutoPanel. Provides the showdialog
    method to construct the controls (if not already
    constructed) and show the dialog; provides the
    hidedialog method to be linked to buttons in the
    dialog that should hide it.
    """
    
    defaultcaption = "Dialog"
    sized = False
    
    def __init__(self, parent, panelclass):
        self._dirty = False
        self._modified = False
        gui.PTopWindow.__init__(self, parent, panelclass)
        
        # Catch the main window closing signal so we can close ourselves
        # (some GUI toolkits don't actually require this, but we do it in
        # all cases for safety and tidiness)
        parent.setup_notify(SIGNAL_CLOSING, self.closedialog)
    
    def _populate_data(self):
        """ Populate the dialog with data. """
        pass
    
    def _retrieve_data(self):
        """ Retrieve data from the dialog. """
        pass
    
    def data_changed(self):
        """ Widget change signals should call this method. """
        self._dirty = True
    
    def showdialog(self):
        """ Populate dialog with data, then show it. """
        if self.shown:
            self._show_window()
        else:
            self._populate_data()
            self.show_init()
    
    def hidedialog(self):
        """ Hide dialog (but don't destroy). """
        self._hide_window()
    
    def closedialog(self):
        """ Close dialog. """
        self.exit()
    
    def dialog_apply(self):
        """ Retrieve dialog data, but keep open. """
        if self._dirty:
            self._retrieve_data()
            self._dirty = False
            self._modified = True
    
    def dialog_ok(self):
        """ Retrieve dialog data, then hide it. """
        if self._dirty:
            self._retrieve_data()
            self._dirty = False
            self._modified = True
        self.hidedialog()
    
    def dialog_cancel(self):
        """ Revert dialog data to original, then hide it. """
        if self._dirty:
            self._populate_data()
            self._dirty = False
        self.hidedialog()

PrefsTabs = [] # this will be filled in dynamically by PPrefsDialog
PrefsMainPanel = [
    get_tabwidget(PrefsTabs, 'main') ]

PrefsButtonPanel = [
    get_padding('buttons'),
    get_action_button(ACTION_APPLY, 'apply'),
    get_action_button(ACTION_OK, 'ok'),
    get_action_button(ACTION_CANCEL, 'cancel') ]

# Helper function for patching frame event handlers into above gui specs
def _update_obj(klass, index, target):
    klass[index][2].update({'target': target})

class PPrefsPanel(gui.PAutoPanel):
    """
    Panel to serve as the overall "frame" of the preferences dialog.
    The _childlist class field should be modified by PPrefsDialog before
    instantiating this class.
    """
    
    childlist = [
        get_toplevel_panel(PrefsMainPanel, ALIGN_JUST, LAYOUT_VERTICAL, 'main'),
        get_toplevel_panel(PrefsButtonPanel, ALIGN_BOTTOM, LAYOUT_HORIZONTAL, 'buttons') ]
    
    def __init__(self, parent):
        gui.PAutoPanel.__init__(self, parent, layout=LAYOUT_VERTICAL,
            margin=framemargin, spacing=panelspacing)
    
    def _createpanels(self):
        _update_obj(PrefsButtonPanel, 1, self._parent.dialog_apply)
        _update_obj(PrefsButtonPanel, 2, self._parent.dialog_ok)
        _update_obj(PrefsButtonPanel, 3, self._parent.dialog_cancel)
        
        super(PPrefsPanel, self)._createpanels()

# Subclass dialog controls to add generic get_value and set_value methods

class PPrefsCheckBox(gui.PCheckBox):
    
    def get_value(self):
        return self.checked
    
    def set_value(self, value):
        self.checked = value

class PPrefsComboBox(gui.PComboBox):
    
    def get_value(self):
        return self.current_text()
    
    def set_value(self, value):
        self.set_current_text(value)

class PPrefsEditBox(gui.PEditBox):
    
    def get_value(self):
        return self.edit_text
    
    def set_value(self, value):
        self.edit_text = value

class PPrefsNumEditBox(gui.PEditBox):
    
    def get_value(self):
        return int(self.edit_text)
    
    def set_value(self, value):
        self.edit_text = str(value)

# Map data types to appropriate controls

controltypes = {
    INI_INTEGER: [PPrefsNumEditBox, (), {'geometry': numeditgeometry()}],
    INI_BOOLEAN: [PPrefsCheckBox, (), {}],
    INI_STRING: [PPrefsEditBox, (), {'geometry': editgeometry()}] }

# Utility function to return INI option control

def get_ini_control(otype, name, target):
    klass, args, kwargs = controltypes[otype]
    kwargs['target'] = target
    return (klass, args, kwargs, name)

class PPrefsDialog(PDialogBase):
    """
    Preferences dialog: takes a parent PMainWindow and
    a PIniFile; constructs a dialog for editing the
    options in the PIniFile, and adds an action to the
    PMainWindow to display the dialog.
    """
    
    defaultcaption = "Preferences"
    panelclass = PPrefsPanel
    
    def __init__(self, parent, inifile, labels):
        self._inifile = inifile
        self._labels = labels
        self.data_map = {}
        
        if hasattr(parent, 'defaultcaption'):
            self.defaultcaption = "%s %s" % (parent.defaultcaption, self.defaultcaption)
        
        # Build the specs from the INI file
        self.spec_sections(PrefsTabs)
        
        # This will now construct the dialog based on the specs
        PDialogBase.__init__(self, parent, self.panelclass)
        
        # Connect the main window's prefs action to show our dialog
        parent.connectaction(ACTION_PREFS, self.showdialog)
        
        # TODO: Fix sizing in wx
    
    def closedialog(self):
        """ Save preferences if modified. """
        if self._modified:
            self._inifile.writeini()
        PDialogBase.closedialog(self)
    
    def _iterate_data(self, scallback, ocallback):
        if scallback is None:
            # We're populating or retrieving, need the actual panel widget
            main = self.clientwidget
        else:
            # We're specifying, need the spec list
            main = self._groups
        inifile = self._inifile
        labels = self._labels
        
        for sname, opts in inifile._optionlist:
            if scallback is not None:
                scallback(main, inifile, labels, sname)
            # TODO: cover other two possible cases for opts tuple
            for oname, otype, odefault in opts:
                if ocallback is not None:
                    attrname = "%s_%s" % (sname, oname)
                    ocallback(main, inifile, labels, attrname, otype)
            if scallback is not None:
                scallback(main, inifile, labels, sname, True)
    
    def _spec_section(self, groups, inifile, labels, sname, done=False):
        # TODO: Add group box control option
        if done:
            self._currentgroup[1][0].append(get_padding(sname))
            if self._currentgroup is not None:
                groups.append(self._currentgroup)
        else:
            self._currentgroup = (labels[sname],
                get_tab_panel([], ALIGN_TOP, LAYOUT_VERTICAL, sname))
    
    def _spec_option(self, groups, inifile, labels, attrname, otype):
        self._currentgroup[1][0].append(get_interior_panel([
                get_label(labels[attrname], attrname),
                get_ini_control(otype, attrname, self.data_changed) ],
            ALIGN_TOP, LAYOUT_HORIZONTAL, attrname))
    
    def spec_sections(self, groups):
        """ Generate the specs for the main panel from the INI file. """
        self._groups = groups
        self._currentgroup = None
        self._iterate_data(self._spec_section, self._spec_option)
        del self._currentgroup
        del self._groups
    
    def _populate_option(self, mainpanel, inifile, labels, attrname, otype):
        control = getattr(mainpanel, attrname)
        value = getattr(inifile, attrname)
        control.set_value(value)
    
    def _populate_data(self):
        """ Populate dialog data from PIniFile object. """
        self._iterate_data(None, self._populate_option)
    
    def _retrieve_option(self, mainpanel, inifile, labels, attrname, otype):
        control = getattr(mainpanel, attrname)
        value = control.get_value()
        setattr(inifile, attrname, value)
    
    def _retrieve_data(self):
        """ Set PIniFile options from dialog data. """
        self._iterate_data(None, self._retrieve_option)
