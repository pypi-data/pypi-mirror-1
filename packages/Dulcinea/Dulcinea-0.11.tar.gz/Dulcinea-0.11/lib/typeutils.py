"""$URL: svn+ssh://svn.mems-exchange.org/repos/trunk/dulcinea/lib/typeutils.py $
$Id: typeutils.py 27513 2005-10-04 20:39:56Z dbinger $

Deprecated.
Use require instead.
"""

def _typename (typespec):
    if isinstance(typespec, type):
        return typespec.__name__
    elif isinstance(typespec, tuple):
        return ' or '.join([t.__name__ for t in typespec])
    else:
        return 'type %s' % typespec

def typecheck (value, typespec, allow_none=0, isinstance=isinstance):
    """(value : any, typespec : type, allow_none : bool = 0)

    Raises TypeError if 'value' does not match 'typespec'.  'typespec' can
    either be a type or a tuple of types.  If allow_none is true then 'value'
    of None is accepted as well.
    """
    if not ((allow_none and value is None) or isinstance(value, typespec)):
        raise TypeError, \
            "required %s, (got %r of type %s)" % (_typename(typespec),
                                                  value,
                                                  type(value).__name__)

def typecheck_seq (value, typespec, allow_none=0):
    """(value : any, typespec : type, allow_none : bool = 0)

    Raises TypeError if 'value' is a sequence and not every element of the
    sequence matches 'typespec'.  If allow_none is true then 'value' of None
    is accepted as well (None for elements is still disallowed).
    """
    if not allow_none and value is None:
        raise TypeError, "required list, got None"
    elif value is not None:
        for item in value:
            if not isinstance(item, typespec):
                raise TypeError, \
                    "required sequence of %s, (got item %r of type %s)" % \
                            (_typename(typespec), item, type(item).__name__)
