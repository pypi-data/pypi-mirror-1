:mod:`pycurry.dbc` --- Design by Contract
=========================================

.. automodule:: pycurry.dbc
    :synopsis: Adds Design by Contract to your functions and classes.

Overview
--------

The basic syntax and functionality of this module is explained in the 
following abstract code example [#fn1]_::

    import pycurry.dbc as dbc # import the dbc-module
    dbc.level.set(dbc.level.max()) # optional: set the effectuation level


    @dbc.dbc_function # decorate free-functions as dbc-functions
    def foo():
        """A free-function has a precondition and a postcondition.
        Both are set to 'True' by default.

        require: True
        ensure: True
        """ 
        pass # body


    class base(object):
        """A class has a class invariant. Set to 'True' by default.

        invariant: True
        """

        __metaclass__ = dbc.dbc_class # initialise class-objects as dbc-classes

        def __init__(self):
            """A constructor, as any function, has a pre-, and postcondition.
            However, the class invariant is evaluated only after execution.

            require: True
            ensure: True
            """
            super(base, self).__init__() # body

        def foo(self):
            """A method, as any function, has a pre-, and postcondition.
            The class invariant is evaluated before and after execution.

            require: True
            ensure: True
            """
            pass # body


    class derived(base):
        """Class invariants are inherited ('and'-ed).

        invariant: True
        """ 

        def __init__(self):
            """A constructor is never an override, so the contracts of the
            constructor of the parent class are not inherited.

            require: True
            ensure: True
            """
            super(derived, self).__init__() # body

        def foo(self):
            """Preconditions are inherited ('or'-ed). The inherited 
            precondition may only be weakened. Postconditions are inherited 
            ('and'-ed). The inherited postcondition may only be strenghtened.

            require_else: True
            ensure_then: True
            """
            pass # body

The following calls will then execute as described:

* ``foo()``:

  #. foo.require
  #. foo.body
  #. foo.ensure

* ``b = base()``:

  #. base.__init__.require
  #. base.__init__.body
  #. base.__init__.ensure
  #. base.invariant

* ``b.foo()``:

  #. base.invariant
  #. base.foo.require
  #. base.foo.body
  #. base.foo.ensure
  #. base.invariant

* ``d = derived()``:

  #. derived.require
  #. base.require
  #. base.__init__.body
  #. base.ensure
  #. derived.__init__.body
  #. derived.ensure
  #. base.invariant and derived.invariant

* ``d.foo()``:

  #. base.invariant and derived.invariant
  #. base.require or derived.require
  #. derived.foo.body
  #. base.ensure and derived.ensure
  #. base.invariant and derived.invariant


.. rubric:: Footnotes

.. [#fn1] For concrete and realistic examples see the :mod:`pycurry.gof` module.

Preconditions
-------------

The precondition of a function is a boolean expression that is evaluated before
the execution of the function. The precondition of a function is therefore the 
obligation of the caller and the benefit of the supplier. If it evaluates to 
``False`` a :class:`precondition_exception` is thrown. 

As the precondition is the obligation of the caller, the supplier must make the 
precondition as visible as itself. This is enforced::

    >>> class c(object):
    ...     __metaclass__ = dbc.dbc_class
    ...     def __query(self):
    ...         return True
    ...     def command(self):
    ...         """
    ...         require: self.__query()
    ...         """
    ...         pass
    ...
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
      File "e:\pycurry\trunk\pycurry\dbc.py", line 597, in __init__
        mcs.scan_pre(func, mcs)
      File "e:\pycurry\trunk\pycurry\dbc.py", line 465, in scan_pre
        pyc.fully_qualified_name(func, cls))
    SyntaxError: supplier '__main__.c.command' is public: precondition must also be public

Preconditions are inherited by overriding methods. Because of the substitution
principle of Liskov they may only be weakened by the overriding method. This
weakening is enforced implicitely by 'or'-ing the precondition of the
overriding method with the precondition of the overriden method. However, 
this implicit weakening is also explicitely enforced within your code::

    >>> class b(object):
    ...     __metaclass__ = dbc.dbc_class
    ...     def foo(self):
    ...         pass
    ...
    >>> class d(b):
    ...     def foo(self):
    ...         """
    ...         require: False
    ...         """
    ...         pass
    ...
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
      File "e:\pycurry\trunk\pycurry\dbc.py", line 597, in __init__
        mcs.scan_pre(func, mcs)
      File "e:\pycurry\trunk\pycurry\dbc.py", line 453, in scan_pre
        pyc.fully_qualified_name(func, cls))
    SyntaxError: supplier '__main__.d.foo' is an override: use 'require_else' instead of 'require'

So the correct code becomes::

    >>> class d(b):
    ...     def foo(self):
    ...         """
    ...         require_else: False
    ...         """
    ...         pass
    ...

Which, when executed, is 'or'-ed as expected::

    >>> d().foo()

Postconditions
--------------

The postcondition of a function is a boolean expression that is evaluated after
the execution of the function. The postcondition of a function is therefore 
the obligation of the supplier and the benefit of the caller. If it evaluates 
to ``False`` a :class:`postcondition_exception` is thrown.

Postconditions are inherited by overriding methods. Because of the substitution
principle of Liskov they may only be strenghtened by the overriding method.
This strengthening is enforced implicitely by 'and'-ing the postcondition of
the the overriding method with the postcondition of the overriden method. 
However, this implicit strengthening is also explicitely enforced within your 
code::

    >>> class b(object):
    ...     __metaclass__ = dbc.dbc_class
    ...     def foo(self):
    ...         pass
    ...
    >>> class d(b):
    ...     def foo(self):
    ...         """
    ...         ensure: False
    ...         """
    ...         pass
    ...
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
      File "e:\pycurry\trunk\pycurry\dbc.py", line 598, in __init__
        mcs.scan_post(func, mcs)
      File "e:\pycurry\trunk\pycurry\dbc.py", line 491, in scan_post
        pyc.fully_qualified_name(func, cls))
    SyntaxError: supplier '__main__.d.foo' is an override: use 'ensure_then' instead of 'ensure'

So the correct code becomes::

    >>> class d(b):
    ...     def foo(self):
    ...         """
    ...         ensure_then: False
    ...         """
    ...         pass
    ...

Which, when executed, is 'and'-ed as expected::

    >>> d().foo()
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
      File "<string>", line 2, in foo
      File "e:\pycurry\trunk\pycurry\dbc.py", line 646, in __proxy
        mcs.parse_post(locs, result, func, mcs)
      File "e:\pycurry\trunk\pycurry\dbc.py", line 576, in parse_post
        raise postcondition_exception(post, func, cls)
    pycurry.dbc.postcondition_exception: supplier '__main__.d.foo' violated postcondition 'False' with client '<stdin>(1): <module>'


Class invariants
----------------

The invariant of a class is a boolean expression that is evaluated after the
creation of an object, just after entering an object and just before leaving
the object again. The class invariant is therefore the obligation of the 
supplier and the benefit of the caller. As such, it can be seen as an 
extension to the postconditions of the methods of the class. If it evaluates 
to ``False`` a :class:`class_invariant_exception` is thrown.

The invariant of a class defines the observable state of an object. Only when 
it is valid, the object can be used. During usage the invariant does not have 
to hold.

Class invariants are inherited by subclasses. Because of the substitution
principle of Liskov they may only be strenghtened by the subclass. This
strengthening is enforced implicitely by 'and'-in the class invariant of the
superclass with the class invariant of the subclass.

Quantifiers
-----------

Two utility quantifiers are available for use in your contracts. They are
provided for those who find list comprehensions less readable.

.. autofunction:: pycurry.dbc.exists
.. autofunction:: pycurry.dbc.forall

Effectuation level
------------------

.. autoclass:: pycurry.dbc.level
    :members: get, set, max, __init__, __enter__, __exit__

Exceptions
----------

.. note::

    You should normally not catch these exceptions as they indicate software
    errors.

.. autoclass:: pycurry.dbc.dbc_exception
.. autoclass:: pycurry.dbc.precondition_exception
.. autoclass:: pycurry.dbc.postcondition_exception
.. autoclass:: pycurry.dbc.class_invariant_exception

