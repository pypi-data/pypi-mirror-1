# Copyright (c) 2008-2009 Luke Stebbing
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

"""
Format a string using names in the current scope.

ScopeFormatter allows Python's string formatting to be used with names
drawn from the current scope, similar to the variable interpolation
found in languages such as Ruby and Perl.


Examples
--------
>>> from scopeformatter import F
>>> greeting = 'Hello'
>>> def greet(name):
...     return F('{greeting}, {name}!')
>>> greet('world')
'Hello, world!'

Positional and keyword arguments are accepted:

>>> F('{greeting} {0} times, {name}!', len(greeting), name='world')
'Hello 5 times, world!'


Requirements
------------
The stack inspection requires a Python VM that provides
`sys._getframe()`, such as CPython.


Limitations
-----------
Non-global names from enclosing scopes will not be found unless
they are referenced in the local scope.

>>> def outer():
...     non_local = 'non-local'
...     def inner():
...         return F('{non_local} is not referenced locally')
...     return inner()
>>> outer()
Traceback (most recent call last):
    ...
KeyError: 'non_local'

>>> def outer():
...     non_local = 'non-local'
...     def inner():
...         non_local
...         return F('{non_local} is referenced locally')
...     return inner()
>>> outer()
'non-local is referenced locally'

"""

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
