# Copyright (c) 2008 Fons Dijkstra
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

"""Adds Design by Contract to your functions and classes.

This implementation tries to be as fully compliant to the Eiffel implementation
of Design by Contract as possible.
"""

import os
import re
import inspect
import threading
import decorator

import pycurry as pyc

class level(object):
    """This level defines which contracts are evaluated at runtime and which 
    not. The following (cumulative) levels are currently defined:

    - ``None``
    - :attr:`require`
    - :attr:`ensure`
    - :attr:`invariant`

    If you donot want to edit the source code you can set the
    :attr:`PYCURRY_DBC_LEVEL` environment variable. This will set the level for
    the whole program except where overruled within the code.

    You can also set the global level within your code. I normally only use 
    this within unittests to ensure that all contracts are evaluated during 
    testing no matter what value :attr:`PYCURRY_DBC_LEVEL` is set to::

        # first set the maximum level
        import pycurry.dbc as dbc
        dbc.level.set(dbc.level.max())

        # only then import the other modules (which might contain contracts)
        import unittest
        import sut 

        class sut_test(unittest.TestCase):
            def test(self):
                pass

        if __name__ == "__main__":
            unittest.main()

    It is also possible to overrule the level for only a specific piece of code
    using a context manager::

        import pycurry.dbc as dbc

        # do not evaluate contracts for the sut module
        with dbc.level(None):
            import sut

    .. note::

        Setting the level has only effect when the interpreter reads your
        source code for the first time. So it can only be set set `once` for 
        a particular function or class and `cannot` be changed at runtime
        afterwards.

    .. todo::
        Per-class level.
    .. todo::
        Check effect of reload()

    .. attribute:: PYCURRY_DBC_LEVEL

        The environment variable to set the global level with. 

    .. attribute:: require

        Only preconditions are checked (default).

    .. attribute:: ensure

        Both pre-, and postconditions are checked.

    .. attribute:: invariant

        Both pre-, postconditions and class invariants are checked.
    """

    PYCURRY_DBC_LEVEL = "PYCURRY_DBC_LEVEL"
    require = "require"
    ensure = "ensure"
    invariant = "invariant"

    @classmethod
    def check(cls, lvl):
        """Checks whether the provided level is a valid one. Throws a 
        ValueError exception when not valid.
        """
        if lvl is not None:
            if str(lvl).lower() not in (
                    cls.require, cls.ensure, cls.invariant):
                raise ValueError("unknown level: %s" % lvl)

    @classmethod
    def max(cls):
        """Returns the maximum level that can be set. Use this within unit 
        tests for example to make sure all contracts will always be checked 
        even if more levels will be added in the future. Currently set to 
        :attr:`invariant`.
        """
        return cls.invariant

    @classmethod
    def get(cls):
        """Get the global level set. Defaults to :attr:`require` if not set.
        """
        result = os.getenv(cls.PYCURRY_DBC_LEVEL, cls.require).lower()
        if result == str(None).lower():
            result = None
        cls.check(result)
        return result

    @classmethod
    def set(cls, lvl = require):
        """Set the new global level. Returns the former level, allowing 
        resetting of the level.
        """
        cls.check(lvl)
        result = cls.get()
        os.environ[cls.PYCURRY_DBC_LEVEL] = str(lvl).lower()
        return result

    def __init__(self, lvl = require):
        """Initialises a level object. Note that the provided level value is
        just local to the created object and not globally set.
        """
        self.check(lvl)
        self.__lvl = lvl
        self.__old = None
        super(level, self).__init__()

    @property
    def lvl(self):
        """The value of this level.
        """
        return self.__lvl

    def __repr__(self):
        return pyc.generic_repr(self)

    def __str__(self):
        return pyc.generic_str(self)

    def __hash__(self):
        return hash(self.__lvl)

    def __eq__(self, other):
        """Tests whether this level equals the other one.
        """
        return isinstance(other, level) and self.lvl == other.lvl

    def __lt__(self, other):
        """Tests whether this level is less then the other one. The following
        order is implemented: None < require < ensure < invariant.
        """
        if not isinstance(other, level):
            raise TypeError("cannot compare with: %s" % other)
        if self.lvl is None:
            result = other.lvl is not None
        elif self.lvl == self.require:
            result = other.lvl in (self.ensure, self.invariant)
        elif self.lvl == self.ensure:
            result = other.lvl == self.invariant
        else:
            result = False
        return result

    def __le__(self, other):
        return self.__lt__(other) or self.__eq__(other)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __gt__(self, other):
        return not self.__le__(other)

    def __ge__(self, other):
        return not self.__lt__(other)

    def __enter__(self):
        """Set the global level to the local one of this object.
        """
        self.__old = self.set(self.lvl)

    def __exit__(self, _1, _2, _3):
        """Reset the global level to the former global level.
        """
        self.set(self.__old)


class dbc_exception(Exception):
    """Base class for all exceptions thrown by this module. It defines
    the following properties/arguments:

    0. :attr:`client` 
    1. :attr:`supplier`
    2. :attr:`condition`

    .. attribute:: client

        The source file location of the calling function.

    .. attribute:: supplier

        The fully qualified name of the called function.

    .. attribute:: condition

        The violated contract.
    """

    def __init__(self, cond, func, cls = None):
        """Initialises the dbc_exception properties. The violated condition of
        the defining function of the (optional) defining class is provided.
        """
        # format the client string
        filename = line = name = None
        for _, filename, line, name, code, _ in inspect.stack():
            if filename != pyc.source_filename(__file__) and code is not None:
                break
        self.client = "%s(%s): %s" % (filename, line, name)
        # format the supplier string
        self.supplier = pyc.fully_qualified_name(func, cls)
        # format the condition string
        self.condition = ""
        for con in cond.strip().split():
            self.condition = "%s %s" % (self.condition, con)
        self.condition = self.condition.strip()
        # initialise the standard exception
        super(dbc_exception, self).__init__(
                self.client, self.supplier, self.condition)


class precondition_exception(dbc_exception):
    """Thrown when a precondition is violated. Note that the client is the
    violator of the condition.
    """

    def __init__(self, cond, func, cls = None):
        """Initialises a precondition_exception object.
        """
        super(precondition_exception, self).__init__(cond, func, cls)

    def __str__(self):
        return "client '%s' violated precondition '%s' of supplier '%s'" \
                % (self.client, self.condition, self.supplier)


class postcondition_exception(dbc_exception):
    """Thrown when a postcondition is violated. Note that the supplier is the
    violator of the condition.
    """

    def __init__(self, cond, func, cls = None):
        """Initialises a postcondition_exception object.
        """
        super(postcondition_exception, self).__init__(cond, func, cls)

    def __str__(self):
        return "supplier '%s' violated postcondition '%s' with client '%s'" \
                % (self.supplier, self.condition, self.client)


class class_invariant_exception(dbc_exception):
    """Thrown when a class-invariant is violated. Note that the supplier is the
    violator of the condition.
    """

    def __init__(self, cond, func, cls = None):
        """Initialises a class_invariant_exception object.
        """
        super(class_invariant_exception, self).__init__(cond, func, cls)

    def __str__(self):
        return "supplier '%s' violated class-invariant '%s' with client '%s'" \
                % (self.supplier, self.condition, self.client)


class tls_condition(threading.local):
    """A thread-private counter that is manipulated by a context manager. It is
    used to disable nested conditions at runtime.
    """

    def __init__(self):
        """Initialises a tls_condition object. Note that this context manager
        holds its own state, so you typically create only one instance.
        """
        try:
            super(tls_condition, self).__init__()
        except TypeError: # bug in coverage
            threading.local.__init__(self)
        self.__eval = 0

    def __enter__(self):
        """Increments the counter by one. Returns boolean indicating whether
        this was the first increment or not.
        """
        self.__eval += 1
        return self.__eval == 1

    def __exit__(self, _1, _2, _3):
        """Decrements the counter by one.
        """
        self.__eval -= 1


class tls_object(threading.local):
    """A thread-private usage counter that is manipulated by a context manager.
    It is used to determine, at runtime, whether to evaluate class-invariants 
    or not.
    """

    def __init__(self):
        """Initialises a tls_object object. Note that this context manager
        holds its own state, so you typically create only one instance.
        """
        try:
            super(tls_object, self).__init__()
        except TypeError: # bug in coverage
            threading.local.__init__(self)
        self.__objs = [] # FILO
        self.__eval = {} # order by object-id

    def use(self, obj):
        """Stores the object to use by the context manager. Returns this
        context manager for your convenience.
        """
        self.__objs.append(id(obj))
        return self

    def __enter__(self):
        """Increments the usage counter of the stored object by one. Returns 
        boolean indicating whether this was the first increment or not.
        """
        obj = self.__objs[-1]
        result = obj not in self.__eval
        if result:
            self.__eval[obj] = 1
        else:
            self.__eval[obj] += 1
        return result

    def __exit__(self, _1, _2, _3):
        """Decrements the usage counter of the stored object by one.
        """
        obj = self.__objs.pop()
        self.__eval[obj] -= 1
        if self.__eval[obj] == 0:
            del self.__eval[obj]


class dbc_class(type):
    """Metaclass for enabling Design by Contract on your own classes.
    """

    inv = re.compile("^\s*%s:(?P<cond>.*)$" % level.invariant, re.MULTILINE)
    pre = re.compile("^\s*%s(?P<inh>_else)?:(?P<cond>.*)$" % level.require,
            re.MULTILINE)
    post = re.compile("^\s*%s(?P<inh>_then)?:(?P<cond>.*)$" % level.ensure,
            re.MULTILINE)
    mangled = re.compile("(^|\W)(?P<name>_{2}\w*[a-zA-Z0-9]_?)(\W|$)")

    @classmethod
    def __scan_attr(mcs, obj, key, value):
        if key not in obj.__dict__:
            try:
                obj.__dict__[key] = value
            except TypeError:
                setattr(obj, key, value)
        else:
            raise ValueError("%s.%s already defined: %s" % (
                pyc.fully_qualified_name(obj), key, getattr(obj, key)))

    @classmethod
    def __scan_doc(mcs, obj):
        if hasattr(obj, "__doc__") and obj.__doc__ is not None:
            result = obj.__doc__
        else:
            result = ""
        return result

    @classmethod
    def __scan_mangled(mcs, mangle, cls = None):
        def __impl(reg):
            return "%s_%s%s%s" % (
                    reg.group(1), cls.__name__, reg.group(2), reg.group(3))
        return (mangle.group("cond") if cls is None else \
                re.sub(mcs.mangled, __impl, mangle.group("cond"))).strip()

    @classmethod
    def __scan_override(mcs, attr, cond, name, cls = None):
        result = False
        if cls is not None and name != "__init__":
            for base in cls.__bases__:
                func = base.__dict__.get(name, None)
                if func is not None:
                    cond += getattr(func, attr, [])
                    result = True
                else:
                    result |= mcs.__scan_override(attr, cond, name, base)
        return result
            
    @classmethod
    def __scan_ast(mcs, cond):
        if cond is None:
            result = (None, None)
        else:
            result = (cond, compile(cond, "<string>", "eval"))
        return result

    @classmethod
    def scan_pre(mcs, func, cls = None):
        """Scan the precondition of the provided function and store them in
        the '__pre__' attribute of the function.
        """
        mcs.__scan_attr(func, "__pre__", [])
        separated = False
        override = mcs.__scan_override(
                "__pre__", func.__pre__, func.__name__, cls)
        for pre in re.finditer(mcs.pre, mcs.__scan_doc(func)):
            if cls is not None and func.__name__ in ("__new__", "__del__"):
                raise SyntaxError(
                    "supplier '%s' is a structor: "
                    "precondition not allowed" %
                        pyc.fully_qualified_name(func, cls))
            elif override and not pre.group("inh"):
                raise SyntaxError(
                    "supplier '%s' is an override: "
                    "use 'require_else' instead of 'require'" %
                            pyc.fully_qualified_name(func, cls))
            elif not override and pre.group("inh"):
                raise SyntaxError(
                    "supplier '%s' is not an override: "
                    "use 'require' instead of 'require_else'" %
                            pyc.fully_qualified_name(func, cls))
            elif cls is not None and \
                    not re.match(mcs.mangled, func.__name__) and \
                    re.search(mcs.mangled, pre.group("cond")):
                raise SyntaxError(
                    "supplier '%s' is public: "
                    "precondition must also be public" %
                            pyc.fully_qualified_name(func, cls))
            else:
                if override and not separated:
                    func.__pre__.append(mcs.__scan_ast(None))
                    separated = True
                func.__pre__.append(mcs.__scan_ast(
                    mcs.__scan_mangled(pre, cls)))

    @classmethod
    def scan_post(mcs, func, cls = None):
        """Scan the postcondition of the provided function and store them in
        the '__post__' attribute of the function.
        """
        mcs.__scan_attr(func, "__post__", [])
        override = mcs.__scan_override(
                "__post__", func.__post__, func.__name__, cls)
        for post in re.finditer(mcs.post, mcs.__scan_doc(func)):
            if cls is not None and func.__name__ in ("__new__", "__del__"):
                raise SyntaxError(
                    "supplier '%s' is a structor: "
                    "postcondition not allowed" %
                        pyc.fully_qualified_name(func, cls))
            elif override and not post.group("inh"):
                raise SyntaxError(
                    "supplier '%s' is an override: "
                    "use 'ensure_then' instead of 'ensure'" %
                            pyc.fully_qualified_name(func, cls))
            elif not override and post.group("inh"):
                raise SyntaxError(
                    "supplier '%s' is not an override: "
                    "use 'ensure' instead of 'ensure_then'" %
                            pyc.fully_qualified_name(func, cls))
            else:
                func.__post__.append(mcs.__scan_ast(
                    mcs.__scan_mangled(post, cls)))

    @classmethod
    def scan_inv(mcs, cls):
        """Scan the class invariant of the provided class and store them in
        the '__inv__' attribute of the class.
        """
        mcs.__scan_attr(cls, "__inv__", [])
        for base in cls.__bases__:
            cls.__inv__ += getattr(base, "__inv__", [])
        for inv in re.finditer(mcs.inv, mcs.__scan_doc(cls)):
            cls.__inv__.append(mcs.__scan_ast(mcs.__scan_mangled(inv, cls)))

    @classmethod
    def scan_locals(mcs, func, spec, *args, **kwargs):
        """Todo.
        """
        # first check for correct population
        min_args = \
                len(spec.args) - (len(spec.defaults) if spec.defaults else 0)
        max_args = len(spec.args)
        act_args = len(args) + len(kwargs)
        if act_args < min_args:
            raise TypeError("%s() takes at least %s argument%s (%s given)" %
                    (func.__name__, min_args,
                     "s" if min_args > 1 else "", act_args))
        if act_args > max_args and \
                spec.varargs is None and spec.keywords is None:
            raise TypeError("%s() takes at most %s argument%s (%s given)" %
                    (func.__name__, max_args,
                     "s" if max_args > 1 else "", act_args))
        for name in kwargs:
            if name not in spec.args and spec.keywords is None:
                raise TypeError("%s() got an unexpected keyword argument %r" %
                        (func.__name__, name))
        # then get the local mapping
        result = {}
        default = 0
        for index, name in enumerate(spec.args):
            if index < len(args):
                result[name] = args[index]
            elif name in kwargs:
                result[name] = kwargs[name]
            else:
                result[name] = spec.defaults[default]
                default += 1
        return result

    @classmethod
    def parse_pre(mcs, locs, func, cls = None):
        """Todo.
        """
        exc = None
        for pre, ast in getattr(func, "__pre__", []):
            try:
                if pre is None:
                    if exc is None:
                        break # precondition satisfied
                    else:
                        exc = None # reset
                else:
                    if not eval(ast, func.func_globals, locs):
                        raise precondition_exception(pre, func, cls)
            except precondition_exception as e:
                if exc is None:
                    exc = e # only remember the first one
        else:
            if exc is not None:
                raise exc # pylint: disable-msg=E0702

    @classmethod
    def parse_post(mcs, locs, result, func, cls = None):
        """Todo.
        """
        locs["__return__"] = result
        for post, ast in getattr(func, "__post__", []):
            if not eval(ast, func.func_globals, locs):
                raise postcondition_exception(post, func, cls)

    @classmethod
    def parse_inv(mcs, locs, func, cls):
        """Todo.
        """
        for inv, ast in getattr(cls, "__inv__", []):
            if not eval(ast, func.func_globals, locs):
                raise class_invariant_exception(inv, func, cls)

    obj = tls_object()
    cond = tls_condition()

    def __init__(mcs, clsname, bases, ns):
        super(dbc_class, mcs).__init__(clsname, bases, ns)
        # always scan the class invariants
        mcs.scan_inv(mcs)
        # decorate all functions with DbC checking
        for name, func in ns.iteritems():
            if inspect.isfunction(func):
                # always scan the contracts
                mcs.scan_pre(func, mcs)
                mcs.scan_post(func, mcs)
                # structor cannot have contracts
                if name not in ("__new__", "__del__"):
                    setattr(mcs, name, mcs.dbc_method(func))

    def dbc_method(mcs, func):
        """Todo.
        """
        # get the argument spec only once, needed for locals
        spec = inspect.getargspec(func)
        # define the proxy as determined by the current level
        lvl = level.get()
        if lvl is None:
            result = func # no proxy needed/wanted
        else:
            if lvl == level.require:
                def __proxy(func, *args, **kwargs):
                    with mcs.cond as evaluate:
                        if evaluate:
                            locs = mcs.scan_locals(func, spec, *args, **kwargs)
                            mcs.parse_pre(locs, func, mcs)
                    return func(*args, **kwargs)
            elif lvl == level.ensure:
                def __proxy(func, *args, **kwargs):
                    with mcs.cond as evaluate:
                        if evaluate:
                            locs = mcs.scan_locals(func, spec, *args, **kwargs)
                            mcs.parse_pre(locs, func, mcs)
                    result = func(*args, **kwargs)
                    with mcs.cond as evaluate:
                        if evaluate:
                            mcs.parse_post(locs, result, func, mcs)
                    return result
            else:
                dynamic = func.__name__ != "__init__"
                def __proxy(func, *args, **kwargs):
                    obj = args[0] # the implicit 'self' parameter
                    with mcs.obj.use(obj) as enter:
                        with mcs.cond as evaluate:
                            if evaluate:
                                locs = mcs.scan_locals(
                                        func, spec, *args, **kwargs)
                                if enter and dynamic:
                                    mcs.parse_inv(locs, func, obj.__class__)
                                mcs.parse_pre(locs, func, mcs)
                        result = func(*args, **kwargs)
                        with mcs.cond as evaluate:
                            if evaluate:
                                mcs.parse_post(locs, result, func, mcs)
                                if enter or not dynamic:
                                    mcs.parse_inv(locs, func,
                                            obj.__class__ if dynamic else mcs)
                        return result
            # decorate the proxy
            result = decorator.decorator(__proxy, func)
        return result


def dbc_function(func):
    """Todo.
    """
    # always scan the contracts
    dbc_class.scan_pre(func)
    dbc_class.scan_post(func)
    # get the argument spec only once, needed for locals
    spec = inspect.getargspec(func)
    # define the proxy as determined by the current level
    lvl = level.get()
    if lvl is None:
        result = func # no proxy needed/wanted
    else:
        if lvl == level.require:
            def __proxy(func, *args, **kwargs):
                with dbc_class.cond as evaluate:
                    if evaluate:
                        locs = dbc_class.scan_locals(
                                func, spec, *args, **kwargs)
                        dbc_class.parse_pre(locs, func)
                return func(*args, **kwargs)
        else:
            def __proxy(func, *args, **kwargs):
                with dbc_class.cond as evaluate:
                    if evaluate:
                        locs = dbc_class.scan_locals(
                                func, spec, *args, **kwargs)
                        dbc_class.parse_pre(locs, func)
                result = func(*args, **kwargs)
                with dbc_class.cond as evaluate:
                    if evaluate:
                        dbc_class.parse_post(locs, result, func)
                return result
        # decorate the proxy
        result = decorator.decorator(__proxy, func)
    return result


def exists(iterable, predicate = bool, *args, **kwargs):
    """Existential quantifier. Tests whether the predicate holds for at least 
    one element of the iterable. The predicate can be any function with any 
    arguments::

        >>> import pycurry.dbc as dbc
        >>> dbc.exists((1, 2), lambda x, y: x == y, 1)
        True
    """
    return bool([item for item in iterable if \
            predicate(item, *args, **kwargs)])

def forall(iterable, predicate = bool, *args, **kwargs):
    """Universal quantifier. Tests whether the predicate holds for all the 
    elements of the iterable. The predicate can be any function with any 
    arguments::

        >>> import pycurry.dbc as dbc
        >>> dbc.forall((1, 2), lambda x, y: x == y, 1)
        False
    """
    return not bool([item for item in iterable if not \
            predicate(item, *args, **kwargs)])

