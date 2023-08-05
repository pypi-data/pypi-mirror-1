"""
$URL: svn+ssh://svn.mems-exchange.org/repos/trunk/dulcinea/lib/param/errors.py $
$Id: errors.py 27392 2005-09-13 14:28:31Z dbinger $
"""

class ParamError (Exception):
    """Base class for all parameter-related exceptions.
    """

class ParamTypeError (ParamError):
    """Raised on violation of the parameter type system, eg. if someone
    passes an integer for a string parameter, or a number for
    a physical_value parameter.
    """

class ConstraintError (ParamError):
    """Raised when attempting to set a parameter value in violation
    of the parameter's constraint.
    """


