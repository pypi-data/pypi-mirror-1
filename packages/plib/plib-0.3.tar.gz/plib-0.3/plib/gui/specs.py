#!/usr/bin/env python
"""
Module SPECS -- GUI Specification Helper Module
Sub-Package GUI of Package PLIB -- Python GUI Framework
Copyright (C) 2008 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains helper variables and functions for
defining GUI specifications that can be used by the PLIB
"auto" GUI classes.
"""

from plib.gui import main as gui

# Control variables for widget geometries; if you want to
# change these values, you can import specs and mutate them
# as long as you do it before any widgets are constructed

framemargin = 10
tabmargin = 10
panelmargin = 4
panelspacing = 10
buttonwidth = 110
combowidth = 90
editwidth = 210
numeditwidth = 80
labelwidth = 150
mainwidth = 400
mainheight = 250

# These are functions rather than static tuples so that the values
# get pulled dynamically from the above variables

button_geometry = lambda: (None, None, buttonwidth, None)
combo_geometry = lambda: (None, None, combowidth, None)
editgeometry = lambda: (None, None, editwidth, None)
numeditgeometry = lambda: (None, None, numeditwidth, None)
labelgeometry = lambda: (None, None, labelwidth, None)
main_geometry = lambda: (None, None, mainwidth, mainheight)

# Convenience functions for building specs

def get_padding(name):
    return ([], (), {}, 'padding_%s' % name)

def get_label(label, name):
    return (gui.PTextLabel, ("%s: " % label,), {'geometry': labelgeometry()},
        'label_%s' % name)

def get_checkbox(label, name):
    return (gui.PCheckBox, (label,), {},
        'checkbox_%s' % name)

def get_combobox(items, name):
    return (gui.PComboBox, (items,), {'geometry': combo_geometry()},
        'combo_%s' % name)

def get_editbox(name, expand=True):
    return (gui.PEditBox, (), {'expand': expand, 'geometry': editgeometry()},
        'edit_%s' % name)

def get_numeditbox(name, expand=True):
    return (gui.PEditBox, (), {'expand': expand, 'geometry': numeditgeometry()},
        'edit_%s' % name)

def get_editcontrol(name, scrolling=True):
    return (gui.PEditControl, (), {'geometry': main_geometry(), 'scrolling': scrolling},
        'text_%s' % name)

def get_button(caption, name, pxname=None):
    return (gui.PButton, (caption, pxname), {'geometry': button_geometry()},
        'button_%s' % name)

def get_action_button(action, name):
    return (gui.PButton, (action, ""), {'geometry': button_geometry()},
        'button_%s' % name)

def get_interior_panel(contents, align, layout, name):
    return (contents, (), {'align': align, 'layout': layout},
        'panel_%s' % name)

def get_midlevel_panel(contents, align, layout, name):
    return (contents, (), {'align': align, 'layout': layout, 'spacing': panelspacing},
        'panel_%s' % name)

def get_tab_panel(contents, align, layout, name):
    return (contents, (), {'align': align, 'layout': layout,
        'margin': tabmargin, 'spacing': panelspacing}, 'panel_%s' % name)

def get_tabwidget(tabs, name):
    return (gui.PAutoTabWidget, (tabs,), {},
        'tabs_%s' % name)

def get_toplevel_panel(contents, align, layout, name):
    return (contents, (), {'align': align, 'layout': layout,
        'margin': panelmargin, 'spacing': panelspacing}, 'panel_%s' % name)
