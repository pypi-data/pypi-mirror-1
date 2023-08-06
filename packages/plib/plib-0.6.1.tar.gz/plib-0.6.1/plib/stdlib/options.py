#!/usr/bin/env python
"""
Module OPTIONS -- Option Parser Utilities
Sub-Package STDLIB of Package PLIB
Copyright (C) 2008-2009 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains a utility function for option parsers, to
reduce the amount of work needed to make use of the optparse
library module. Instead of having to manually instantiate an
option parser, add options to it, then call its parsing method,
the parse_options function wraps it all into one package; you
give it a list of option parameters and arguments and it
returns the parsed (options, args) tuple. This also allows
adding argument checking functionality.
"""

import optparse
from itertools import imap

# Usage format string -- optparse will replace the %prog
usage = "usage: %prog [options]"

def _argstring(args):
    if isinstance(args, basestring):
        return args
    # We'd prefer a genexp here but we want to be usable
    # if version < 2.4
    return " ".join(imap(str, args))

def parse_options(optlist, arglist=[]):
    """
    Function to add each option in optlist to the OptionParser and then return
    the parsing results to the program; expects optlist to be a sequence (can be
    list or tuple) of 3-tuples: short name, long name, dict of keyword arguments.
    
    Also checks for correct number of arguments if passed a list of argument
    names in arglist; if arglist is a single string, it is added to the usage
    string but is not used to check the command line.
    """
    
    global usage
    if arglist:
        usage = " ".join([usage, _argstring(arglist)])
    optparser = optparse.OptionParser(usage)
    for shortopt, longopt, kwargs in optlist:
        optparser.add_option(shortopt, longopt, **kwargs)
    retval = optparser.parse_args()
    if not isinstance(arglist, basestring):
        l1 = len(retval[1])
        l2 = len(arglist)
        if l1 != l2:
            optparser.error("Invalid arguments: %i received, %i expected." % (l1, l2))
    return retval
