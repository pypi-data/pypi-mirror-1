"""Format a string using names in the current scope."""

from sys import _getframe

def F(*args, **kwds):
    """
    Format a string using names in the caller's scope.

    Names are looked up in the keyword arguments, then in the caller's
    locals, and finally in the caller's globals.

    Raises `KeyError` if a name is not found.

    """
    if not args:
        raise TypeError('F() takes at least 1 argument (0 given)')
    caller = _getframe(1)
    names = {}
    names.update(caller.f_globals)
    names.update(caller.f_locals)
    names.update(kwds)
    return args[0].format(*args[1:], **names)
