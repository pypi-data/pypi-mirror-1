"""$URL: svn+ssh://svn.mems-exchange.org/repos/trunk/dulcinea/lib/sort.py $
$Id: sort.py 27538 2005-10-11 23:00:36Z rmasse $

Utility functions for sorting sequences.
"""

import re
from quixote.html import stringify

def sort(seq):
    """(seq) -> [any]

    Sort 'seq', which must be a sequence object of any type.
    If 'seq' is a list object, it will be sorted in-place and returned.
    Otherwise, 'seq' will be converted to a list, sorted in-place,
    and returned.

    Don't just use 'sort(list)' instead of 'list.sort()'; the latter
    makes it clear that an existing list is being sorted in-place.
    Instead, replace code like this:
      k = dict.keys() ; k.sort()
      values = list(object.get_some_funky_sequence()) ; values.sort()
    with code like this:
      k = sort(dict.keys())
      values = sort(object.get_some_funky_sequence())
    """
    if not isinstance(seq, list):
        seq = list(seq)
    seq.sort()
    return seq

def _sort_and_undecorate(dlist):
    dlist.sort()
    list = [val for (_, val) in dlist]
    return list

def str_sort(seq):
    """(seq) -> []

    Sort 'seq' by the str() of each element.
    """
    dlist = [(stringify(val), val) for val in seq]
    return _sort_and_undecorate(dlist)

def lexical_sort(seq):
    """(seq) -> []

    Sort 'seq' by the stringify().lower() of each element.
    """
    dlist = [(stringify(val).lower(), val) for val in seq]
    return _sort_and_undecorate(dlist)

def attr_sort(seq, attr):
    """(seq, attr : string) -> []

    Sort 'seq' by the attribute 'attr' of each element.
    """
    dlist = [(getattr(val, attr), val) for val in seq]
    return _sort_and_undecorate(dlist)

def lex_attr_sort(seq, attr):
    """(seq, attr : string) -> []

    Sort 'seq' by the stringify().lower() of the 'attr' attribute of each
    element.
    """
    dlist = [(stringify(getattr(val, attr)).lower(), val) for val in seq]
    return _sort_and_undecorate(dlist)

def method_sort(seq, method):
    """(seq, method : string) -> []

    Sort 'seq' by the result of calling method 'method' on each element.
    """
    method_name = stringify(method)
    dlist = [(getattr(val, method_name)(), val) for val in seq]
    return _sort_and_undecorate(dlist)

def function_sort(seq, func):
    """(seq, func : function) -> []

    Sort 'seq' by the result of calling 'func' on each element.
    """
    dlist = [(func(val), val) for val in seq]
    return _sort_and_undecorate(dlist)


number_re = re.compile(r'\s*(\d+)|(\d*\.\d+)\s*')

def natural_sort(seq, strfunc=stringify):
    """(seq, strfunc : function) -> []

    Sort a list of items in a human friendly way.  Strings are sorted as
    usual, except that decimal integer substrings are compared on their
    numeric value.  For example,

        a < a0 < a1 < a1a < a1b < a2 < a10 < a20

    Strings can contain several number parts:

        x2-g8 < x2-y7 < x2-y08 < x8-y8

    in which case numeric fields are separated by nonnumeric characters.
    Leading spaces are ignored. This works very well for IP addresses from
    log files, for example.

    Numeric substrings with decimal points are treated as floating point.

        1.001 < 1.002 < 1.010 < 1.02 < 1.1 < 1.3

    This function was inspired by the Mac "Natural Order" utility.  It
    does not match the Natural Order algorithm exactly and probably could
    use improvements.
    """
    dlist = []
    for item in seq:
        parts = []
        s = strfunc(item)
        while s:
            m = number_re.search(s)
            if not m:
                parts.append(s)
                break
            else:
                parts.append(s[:m.start()])
                if m.group(1):
                    val = int(s[m.start(1):m.end(1)])
                else:
                    val = float(s[m.start(2):m.end(2)])
                parts.append(val)
                s = s[m.end():]
        dlist.append((filter(None, parts), item))
    return _sort_and_undecorate(dlist)
