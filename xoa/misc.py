#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Miscellaneaous low level utilities
"""
# Copyright or © or Copr. Shom/Ifremer/Actimar
#
# stephane.raynaud@shom.fr, charria@ifremer.fr, wilkins@actimar.fr
#
# This software is a computer program whose purpose is to [describe
# functionalities and technical features of your software].
#
# This software is governed by the CeCILL license under French law and
# abiding by the rules of distribution of free software.  You can  use,
# modify and/ or redistribute the software under the terms of the CeCILL
# license as circulated by CEA, CNRS and INRIA at the following URL
# "http://www.cecill.info".
#
# As a counterpart to the access to the source code and  rights to copy,
# modify and redistribute granted by the license, users are provided only
# with a limited warranty  and the software's author,  the holder of the
# economic rights,  and the successive licensors  have only  limited
# liability.
#
# In this respect, the user's attention is drawn to the risks associated
# with loading,  using,  modifying and/or developing or reproducing the
# software by the user in light of its specific status of free software,
# that may mean  that it is complicated to manipulate,  and  that  also
# therefore means  that it is reserved for developers  and  experienced
# professionals having in-depth computer knowledge. Users are therefore
# encouraged to load and test the software's suitability as regards their
# requirements in conditions enabling the security of their systems and/or
# data to be ensured and,  more generally, to use and operate it in the
# same conditions as regards security.
#
# The fact that you are presently reading this means that you have had
# knowledge of the CeCILL license and that you accept its terms.

import types


def is_iterable(obj, nostr=True, nogen=True):
    """Check if an object is iterable or not

    Parameters
    ----------
    obj:
        Object to check

    Return
    ------
    bool
    """

    if not nogen and isinstance(obj, types.GeneratorType):
        return True
    if not (hasattr(obj, '__len__') and callable(obj.__len__)):
        return False
    if nostr:
        return not isinstance(obj, str)
    return True


def dict_filter(kwargs, filters, defaults=None, copy=False, short=False,
                keep=False, **kwadd):
    """Filter out kwargs (typically extra calling keywords)

    Parameters
    ----------
    kwargs:
        Dictionnary to filter.
    filters:
        Single or list of prefixes.
    defaults:
        dictionnary of default values for output fictionnary.
    copy:
        Simply copy items, do not remove them from kwargs.
    short:
        Allow prefixes to not end with ``"_"``.
    keep:
        Keep prefix filter in output keys.

    Example
    -------
    >>> kwargs = {'basemap':'f', 'basemap_fillcontinents':True,
    ... 'quiet':False,'basemap_plot':False}
    >>> print kwfilter(kwargs,'basemap',
    ... defaults=dict(drawcoastlines=True,plot=True), good=True)
    {'plot': False, 'fillcontinents': True, 'good': True, 'basemap': 'f',
    'drawcoastlines': True}
    >>> print kwargs
    {'quiet': False}

    Return
    ------
    dict
    """

    if isinstance(filters, str):
        filters = [filters]
    if copy:
        kwread = kwargs.get
    else:
        kwread = kwargs.pop

    # Set initial items
    kwout = {}
    for filter_ in filters:
        if not filter_.endswith('_') and filter_ in kwargs:
            if isinstance(kwargs[filter_], dict):
                kwout.update(kwread(filter_))
            else:
                kwout[filter_] = kwread(filter_)
        if not short and not filter_.endswith('_'):
            filter_ += '_'
        for att, val in kwargs.items():
            if att.startswith(filter_) and att != filter_:
                if keep:
                    kwout[att] = kwread(att)
                else:
                    kwout[att[len(filter_):]] = kwread(att)

    # Add some items
    kwout.update(kwadd)

    # Set some default values
    if defaults is not None:
        for att, val in defaults.items():
            kwout.setdefault(att, val)
    return kwout


def match_string(ss, checks, ignorecase=True, transform=None):
    """Check that a string verify a check list that consists of
    a list of either strings or callables

    Parameters
    ----------
    ss: str
    checks: str, callable, list of {str or callable}
    ignorecase: bool
    transform: callable

    Example
    -------
    >>> match_string('sst', 'sst')
    True
    >>> match_string('sst', [re.compile(r'ss.$').match])
    True

    Return
    ------
    True
    """
    # Nothing
    if not ss or not checks:
        return False

    # Setup
    ss = ss.strip()
    if ignorecase:
        ss = ss.lower()
    if not is_iterable(checks, nogen=False):
        checks = [checks]
    checks = [x for x in checks if x is not None]

    # Callables
    sss = []
    for check in checks:
        if callable(transform) and not callable(check):
            check = transform(check)
        if callable(check) and check(ss):
            return True
        if isinstance(check, str):
            sss.append(check)

    # Strings
    sss = [s.strip() for s in sss]
    if ignorecase:
        sss = [s.lower() for s in sss]
    return ss in sss


def match_attrs(obj, checks, name=True, ignorecase=True, transform=None):
    """Check that at least one of the attributes matches check list

    Parameters
    ----------
    obj: object
    checks: dict
        A dictionary of (attribute name, checklist), checklist being an
        iterable as accepted by :func:`match_string`.
    """
    if obj is None or checks is None:
        return False
    for attname, attchecks in checks.items():
        if (hasattr(obj, attname) and
            match_string(getattr(obj, attname), attchecks,
                         ignorecase=ignorecase, transform=transform)):
            return True
    return False


class ArgList(object):
    """Utility to always manage arguments as list and return results as input

    Examples
    --------
    >>> a = 'a'
    >>> al = ArgList(a)
    >>> al.get() # input for function as list
    ['a']
    >>> al.put(['aa']) # output as input
    'aa'

    >>> a = ['a','b']
    >>> al = ArgList(a)
    >>> al.get()
    ['a', 'b']
    >>> al.put(['aa'])
    ['aa']

    """

    def __init__(self, argsi):
        self.single = not isinstance(argsi, list)
        self.argsi = argsi

    def get(self):
        return [self.argsi] if self.single else self.argsi

    def put(self, argso):
        so = not isinstance(argso, list)
        if (so and self.single) or (not so and not self.single):
            return argso
        if so and not self.single:
            return [argso]
        return argso[0]


class ArgTuple(object):
    """Utility to always manage arguments as tuple and return results as input

    :Examples:

        >>> a = 'a'
        >>> al = ArgTuple(a)
        >>> al.get() # input for function as tuple
        ['a']
        >>> al.put(['aa']) # output as input
        'aa'

        >>> a = ['a','b']
        >>> al = ArgTuple(a)
        >>> al.get()
        ['a', 'b']
        >>> al.put(['aa'])
        ['aa']

    """

    def __init__(self, argsi):
        self.single = not isinstance(argsi, tuple)
        self.argsi = argsi

    def get(self):
        return (self.argsi, ) if self.single else self.argsi

    def put(self, argso):
        so = not isinstance(argso, tuple)
        if (so and self.single) or (not so and not self.single):
            return argso
        if so and not self.single:
            return (argso, )
        return argso[0]
