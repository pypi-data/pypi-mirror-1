===================
SEXpy User's Manual
===================

SEXpy is an alternate S-expression syntax for the Python language.

.. contents::


Synopsis
========

.. parsed-literal::

    $ ./sex.py
    SEXpy> (def (square x) (return (* x x)))
    SEXpy> (square 2)
    4
    SEXpy> (exit)


Executing SEXpy code
====================

The easiest way to execute a SEXpy script is to use ``sex.py`` utility::

    $ sex.py myscript.sex

SEXpy scripts can be also compiled to Python bytecode::

    $ sex.py -c myscript.sex
 
The resulting bytecode file can be imported from a Python program or executed
as a standalone script::

    $ python myscript.pyc


Interactive shell
=======================

Launching sex.py without arguments will give you an interactive shell. There is
nothing special about it - just enter some expressions and see what happens.


Using SEXpy from Python programs
================================

Importing SEXpy modules
-----------------------

Besides importing Python modules from SEXpy it is also possible to import SEXpy
files from a Python program::

    >>> from sexpy import import_file
    >>> foo = import_file('examples/foo.sex')
    >>> foo.bar()
    Test passed! ;-)

It is also possible to compile SEXpy code to Python bytecode::

    $ sex.py -c foo.sexpy

The resulting ``.pyc`` file can be imported juat like a regular module::

    >>> import foo
    >>> foo.bar()
    Test passed! ;-)

``.pyc`` files can also be executed like a regular Python scripts::

    $ python foo.pyc
    Test passed! ;-)

Constructiong SEXpy code in runtime
-----------------------------------
from sexpy import import_file
It is possible to construct SEXpy code in runtime. The rules are simple:

    - SEXpy code is just a Python list
    - use plain numbers for numeric literals
    - use sexpy.String for string literals
    - use sexpy.List for list literals

Here is what is looks like::

    from sexpy import compile, String as S
    
    code = [
        ['=', 's', ['%', S("2 * 2 = %i"), ['*', 2, 2]]],
        ['print', 's'],
    ]
    exec compile(code)
