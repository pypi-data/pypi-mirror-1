======================
SEXpy Syntax Reference
======================

SEXpy basically a straightforward translation of Python into S-expressions.


Literal values
==============
SEXpy understands the following types of literal values:

:names: ``foo``
:integers: ``123``
:long integers: ``1000L``
:floats: ``100.3e4``
:strings: ``"I'm a string!"``
:lists: ``#(a b c)``

Unicode strings and dictionary literals are not (yet) supported. String escapes
are also not supported, all strings in SEXpy behave like raw strings in Python.


Comments
========

Comments start with a semicolon Pythonic string comments work too::

    ; What happen ?
    (print "All you base are belong to us.") ; Ha Ha Ha Ha ....
    
    "For great justice."

Function calls
==============

``hello(a, b, spam)`` becomes ``(hello a b spam)``

Keyword arguments (and many other things) are not (yet) supported.


Attribute access
================

``foo.bar`` becomes ``(. foo bar)`` and ``foo.bar.baz`` becomes ``(. (. foo
bar) baz)``. ``bar`` and ``baz`` must be plain names here, while ``foo`` can be an
arbitrary expression.

To avoid unnessessary verbosity SEXpy supports ``foo.bar.baz`` notation (where
``foo``, ``bar``, and ``baz`` are plain names). In other words, Python's
``s.strip()`` can be written either as ``(s.strip)`` or as ``((. s strip))``,
while for ``s.strip().toupper()`` you have to write ``((. (. s strip)
toupper))``.


Item access
===========

``object[index]`` becomes ``(.. object index)`` which is ultimately unpythonic
and counter-intuitive. If you can imaging some better syntax, let us know. :)


Operators
=========

Most Python's arythmetic and comparison operators (``+``, ``-``, ``>``, ``<``,
etc.) are supported. The syntax is the same as for function calls: ``x * 2``
becomes ``(+ x 2)``. Note that Python binary operators are still binary in
SEXpy, so you have to write ``a1 * a2 * a3`` as ``(* (* a1 a2) a3)`` (this may
be changed in future versions of SEXpy). Also note that despite the syntax
these operators are not first class functions in SEXpy (as well as in Python).
If you want them to be functions, you probably need to have a look at
``operator`` module.


String interpolation
====================

``"x = %i" % x"`` becomes ``(% "x = %i" x)``.


Module imports
==============

Use ``(import foo bar baz)`` instead of ``import
foo, bar, baz``. Instead of ``from spam import eggs`` use ``(from spam import
eggs)``. ``import`` keyword is just a syntax sugar here and can be omitted
giving ``(from spam eggs)``.


Raising exceptions
==================

Just use ``(raise SomeException)``. Of course, ``(raise (SomeException "Bad
Thing happened"))`` is also possible.

Ironically, ``try``, ``except`` and ``finally`` are not (yet) supported. Stay
tuned. :)


``if`` statement
================

``if`` statement has the following syntax:

.. parsed-literal::

    (if
        (*condigion1* *statement1* ...)
        (*condigion1* *statement2* ...)
        (else *statements3*))

It is similar to Lisp's ``cond``.

Example::
    
    if t >= 0:
        print "Nice weather!"
        go_for_a_walk()
    elif t < 0:
        print "Winter the Matushka has come!"
    else:
        print "Time to take some more red pills"

becomes::

    (if ((>= t 0)
        (print "Nice weather!")
        ((go_for_a_walk)))
    ((< t 0)
        (print "Winter the Matushka has come!"))
    (else
        (print "Time to take some more red pills")))
        

``for`` statement
=================

``for`` statement in SEXpy has the following syntax:

.. parsed-literal::

    (for *variable* *list* *statement1* *statement2* ...)

Python's ``for i in [1, 2, 3]: print i`` becomes ``(for i #(1 2 3) (print i))``. ``else`` clause is not supported.


Function definitions
====================

Function definitions are Scheme-style::

    (def (hello name)
        (print (% "Hello %s!" name))
        (print "Nice to meet you."))

Use ``(return something)`` to return a value::

    (def (square x)
        (return (* x x)))

``yield`` is also supported::

    (def (squares n)
        (for i (range n)
            (yield (* i i))))


Class definitions
=================

The general syntax is:

.. parsed-literal::

    (class (*classname* *baseclass1* *baseclass2* ...)
        *statement1*
        *statement2*
        ...)

Here is an example::

    class Egg(object):
        def __init__(self, animal):
            self.animal = animal
        def __str__(self):
            return "The amazing %s's egg!" % self.animal

becomes::

    (class (Egg object)
        (def (__init__ self animal)
            (= (. self animal) animal))
        (def (__str__ self)
            (return (% "The amazing %s's egg!" (. self animal)))))
