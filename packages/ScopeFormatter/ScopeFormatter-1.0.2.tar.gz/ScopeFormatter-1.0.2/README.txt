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
``sys._getframe()``, such as CPython.


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
