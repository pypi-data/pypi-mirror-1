#!/usr/bin/env python
"""
Sub-Package STDLIB of Package PLIB -- Python Standard Library Extensions
Copyright (C) 2008-2009 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This sub-package contains classes and functions which extend or
modify the Python standard library.

Note that, as with the PLIB.CLASSES sub-package, the ModuleProxy
class from the PLIB.UTILS sub-package is used to put the sub-modules
of this package in the package namespace, so that you can write,
for example,

    from plib.stdlib import abstractcontainer

instead of having to write

    from plib.stdlib.abstractcontainer import abstractcontainer

See the PLIB.CLASSES sub-package docstring and comments for more details.

This file itself currently includes:

variables pythonpath, plibpath, binpath, sharepath --
    contain pathnames to root python directory, plib directory,
    third-party binary directory, and third-party shared data directory
    (the latter two are where plib's scripts and example programs will
    have been installed)

functions any, all -- a little different from the functions built in
    to Python 2.5, these allow an optional predicate

function closure -- similar to functools.partial from Python 2.5; returns
    a callable object that returns the same result as calling the passed
    function with the passed arguments (but does not allow additional
    arguments with the actual call, as functools.partial does)

function dotted_import -- wraps the __import__ builtin so that it
    returns the 'innermost' module in a dotted name; the equivalent
    of 'import x.y.z'

function dotted_from_import -- dotted_import, plus a getattr call to
    retrieve the named attribute from the dotted module; the equivalent
    of 'from x.y.z import a' (except that module a of package x.y.z
    will not be returned unless it has already been imported into the
    namespace of x.y.z)

function first -- returns first item in iterable, or default if empty.

function inrange -- returns index forced to be >= low, <= high.

function inverted -- returns the inverse of a mapping.

function iterfile --

Returns a generator that can be used in place of "for line in file"
in cases (such as when stdin is the file) where Python's line buffering
might mean the program doesn't get the lines one at a time as they come,
but in bunches. See

http://utcc.utoronto.ca/~cks/space/blog/python/FileIteratorProblems

for a discussion of this issue and the code for this function that
fixes it. Note that the issue can also arise, as the blog entry notes,
with line-oriented network protocols, which means any time you are
using a "file-like object" derived from a socket.

function last -- returns last item in iterable, or default if empty.

function normalize -- returns index with negative values normalized
    relative to count.

function normalize_slice -- returns a list of indexes "covered" by a
    slice (normalized relative to count), or an integer giving the
    index to which a zero-length slice refers (normalized relative
    to count).

function slice_len -- returns the "length" of a slice (meaning the
    number of indexes that would be affected if it were used as an
    index into a sequence).

function sorted -- backports the builtin to Python versions < 2.4. No
    reverse functionality for earlier versions.

functions strtobool, strtodate -- self-explanatory.

function cached_property (and auxiliary class CachedProperty) --

Implementation of a "cached property" descriptor, which
does the following: on first access, it does a (presumably
expensive) calculation to determine the property's value,
and then "caches" the value in the instance as a plain
attribute, so further lookups will get the attribute
directly without the function call overhead of the
descriptor. Note that this means this must be a non-data
descriptor (because data descriptors, such as properties,
can't be masked by an ordinary instance attribute). This
also means, of course, that the "cached property" should
never be written to (it can be, but doing so wipes out
the cached value with no way of recovering it).

Note: the functionality has been split between a descriptor
class and a public decorator-usable function, but that is
not strictly necessary (since classes can be used as
decorators). Splitting it this way allows for a use case
where the class is called directly and the property name is
supplied explicitly (in which case there is no need for the
class to be cluttered with code to magically extract the
name from the fget function).

Also note that, unlike the standard property function, there
would be no real benefit in implementing cached_property in
a C extension module; the main reason for doing that would
be speed, but since the whole point is to eliminate the
overhead of the property altogether after the first access,
the additional overhead of a Python class instance is
negligible compared to the (presumably expensive) initial
calculation of the property value.
"""

import sys
import os
import datetime
import glob
from itertools import ifilter, ifilterfalse

from plib.utils import ModuleProxy

from _paths import *
from SortMixin import SortMixin

def any(iterable, predicate=bool):
    """ Return True if any element of iterable satisfies predicate. """
    for element in ifilter(predicate, iterable):
        return True
    return False

def all(iterable, predicate=bool):
    """ Return True only if all elements of iterable satisfy predicate. """
    for element in ifilterfalse(predicate, iterable):
        return False
    return True

def closure(fn, *args, **kwargs):
    """ Return a no-parameter callable equivalent to fn(*args, **kwargs). """
    def f():
        return fn(*args, **kwargs)
    return f

def dotted_import(name):
    """ Returns the module pointed to by import x.y.z. """
    mod = __import__(name)
    components = name.split('.')
    for comp in components[1:]:
        mod = getattr(mod, comp)
    return mod

def dotted_from_import(modname, attrname):
    """ Returns the module attribute pointed to by from x.y.z import a. """
    return getattr(dotted_import(modname), attrname)

def first(iterable, default=None):
    """ Return first item in iterable, or default if empty. """
    for item in iterable:
        return item
    return default

def inrange(index, v1, v2):
    """ Force index to be within the range v1 to v2, and return result. """
    if v1 < v2:
        low = v1
        high = v2
    else:
        low = v2
        high = v1
    return min(max(index, low), high)

if sys.version_info < (2, 4):
    
    def inverted(mapping, keylist=None):
        """
        Return a dict that is the inverse of the given mapping. The
        optional argument keylist limits the keys that are inverted.
        
        This version is for Python 2.3 and earlier and uses a for
        loop to avoid making an extra in-memory copy of the mapping
        (for the intermediate sequence of inverted value, key tuples)
        as a list comprehension or built-in function such as zip
        would do. This implementation is significantly slower than
        the Python 2.4 and later implementation using generator
        expressions.
        """
        
        result = mapping.__class__()
        if keylist is not None:
            for key in keylist:
                result[mapping[key]] = key
        else:
            for key, value in mapping.iteritems():
                result[value] = key
        return result

else:
    
    def inverted(mapping, keylist=None):
        """
        Return a dict that is the inverse of the given mapping. The
        optional argument keylist limits the keys that are inverted.
        
        Note that we use a generator expression and iteritems to avoid
        making an extra in-memory copy of the mapping (for the intermediate
        sequence of inverted value, key tuples). This version only works
        for Python 2.4 and later.
        """
        
        if keylist is not None:
            return mapping.__class__((mapping[key], key) for key in keylist)
        else:
            return mapping.__class__((value, key) for key, value in mapping.iteritems())

def iterfile(f):
    """
    Returns a generator that yields lines from a file as "for line in file"
    does, but avoids potential problems with buffering. Use as
    
    for line in iterfile(file):
    """
    while 1:
        line = f.readline() # this guarantees getting each line when it's ready
        if not line:
            return # we've reached EOF
        yield line

def last(iterable, default=None):
    """ Return last item in iterable, or default if empty. """
    result = default
    for item in iterable:
        result = item
    return result

def normalize(count, index):
    """
    Return index value with negative indexes converted to indexes
    relative to endpoint. Index values out of range after conversion
    will raise IndexError.
    """
    
    if index < 0:
        result = index + count
    else:
        result = index
    if (result < 0) or (result > count - 1):
        raise IndexError, "sequence index out of range"
    return result

def normalize_slice(count, index):
    """
    Return one of the following, depending on the type of slice index:
    
    -- For a non-empty slice (e.g., [x:y] where x != y), return a list of
       indexes to be affected;
    
    -- For an empty slice (e.g., [x:x]), return the slice location (x)
       as an int.
    
    -- For extended slices, if start and stop are the same, return an
       empty list; otherwise treat as a non-empty slice.
    
    The index(es) returned will be normalized relative to count, and indexes
    out of range after normalization will be truncated to range(0, count + 1).
    The extra index at count is to allow for the possibility of an append
    (a zero-length slice with index == count). Note that this means that,
    unlike the normalize function above, this function will never throw an
    exception due to values being out of range; this is consistent with the
    observed semantics of Python slice syntax, where even values way out of
    range are accepted and truncated to zero or the end of the sequence.
    The only exception this routine will throw is ValueError for a zero
    slice step.
    """
    
    if index.step is None:
        step = 1
    else:
        step = int(index.step)
    if step == 0:
        raise ValueError, "Slice step cannot be zero."
    if index.start is None:
        if step < 0:
            start = count - 1
        else:
            start = 0
    else:
        start = int(index.start)
        if start < 0:
            start += count
    if index.stop is None:
        if step < 0:
            stop = -1
        else:
            stop = count
    else:
        stop = int(index.stop)
        if stop < 0:
            stop += count
    if start == stop:
        if step != 1:
            return []
        return inrange(start, 0, count)
    elif ( (count == 0) or
        ((step > 0) and ((start >= count) or (start > stop))) or
        ((step < 0) and ((start < 0) or (start < stop))) ):
            return []
    else:
        start = inrange(start, 0, count - 1)
        if step < 0:
            stop = inrange(stop, -1, count - 1)
        else:
            stop = inrange(stop, 0, count)
        return range(start, stop, step)

def slice_len(s):
    """
    Return the number of indexes referenced by a slice. Note that
    we do not normalize the slice indexes, since we don't have a
    sequence length to reference them to. Also note that, because
    of this, we have to return None if there is no stop value, or
    if start or stop are negative.
    """
    
    if s.start is None:
        start = 0
    else:
        start = int(s.start)
    if start < 0:
        return None
    if s.stop is None:
        return None
    stop = int(s.stop)
    if stop < 0:
        return None
    if s.step is None:
        step = 1
    else:
        step = int(s.step)
    if step == 0:
        raise ValueError, "Slice step cannot be zero."
    if start == stop:
        return 0
    else:
        return (stop - start) // step

if sys.version < 2.4:
    
    class _sorted_helper(SortMixin, list): pass
    
    def sorted(iterable, sortfunc=None, key=None):
        if isinstance(iterable, list):
            result = iterable[:]
            if sortfunc is None:
                if key is not None:
                    sortfunc = lambda x, y: cmp(key(x), key(y))
            if sortfunc is None:
                result.sort()
            else:
                result.sort(sortfunc)
            return result
        else:
            result = _sorted_helper()
            for item in iterable:
                result.insert_sorted(item, sortfunc, key)
            return list(result)

else:
    
    from __builtin__ import sorted

def strtobool(s):
    """
    Return bool from string s interpreting s as a 'Python value string'.
    Return None if s is not 'True' or 'False'.
    """
    
    if s == 'True':
        return True
    if s == 'False':
        return False
    return None

def strtodate(s):
    """ Return date object from string s formatted as date.__str__ would return """
    
    dateargs = s.split("-")
    return datetime.date(int(dateargs[0]), int(dateargs[1]), int(dateargs[2]))

class CachedProperty(object):
    """
    Non-data descriptor class for cached property. The
    expected typical use case is to be called from the
    cached_property function, which generates the name of
    the property automatically, but the class can also be
    instantiated directly with an explicit name supplied.
    """
    
    def __init__(self, aname, fget, doc=None):
        self.aname = aname
        self.fget = fget
        self.__doc__ = doc
    
    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        result = self.fget(obj)
        setattr(obj, self.aname, result)
        return result

def cached_property(fget, doc=None):
    """
    Function to return cached property instance. We need
    this as a wrapper to supply the name of the property by
    magic rather than force the user to enter it by hand;
    this is done by looking up the name of the fget function
    (which also allows this function to be used as a decorator
    and have the intended effect).
    """
    
    if doc is None:
        doc = fget.__doc__
    return CachedProperty(fget.__name__, fget, doc)

# *************** end of 'internal' functions for this module ***************

# Now we do the ModuleProxy magic to make classes in
# our sub-modules appear in our namespace

# Helper function to actually do the import when the
# module attribute is accessed; note that it assumes
# that the function returns the actual class defined
# in the module, not the module itself, and it assumes
# that the class will have the same name as the module

def module_helper(modname):
    def f():
        result = __import__(modname, globals(), locals())
        return getattr(result, modname)
    f.__name__ = "%s_helper" % modname
    return f

# Generate a dictionary of module names and classes
# in our sub-package; note that here (unlike in the
# CLASSES sub-package) we have a few modules we want
# to exclude because we actually want them to appear
# in our namespace as modules, not classes

excludes = ['__init__', 'coll', 'options']
module_dict = {}
for pathname in __path__:
    for filename in glob.glob(os.path.join(pathname, "*.py")):
        modname = os.path.splitext(os.path.basename(filename))[0]
        if modname not in excludes:
            module_dict[modname] = module_helper(modname)

# Now do the module proxy -- see comments in the CLASSES
# sub-package for caveats when doing this

ModuleProxy(__name__, module_dict)

# Now clean up our namespace
del glob, ModuleProxy, module_helper, module_dict, \
    pathname, filename, modname
