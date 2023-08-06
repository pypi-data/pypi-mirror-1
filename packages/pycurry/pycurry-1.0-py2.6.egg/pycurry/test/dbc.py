"""Tests for the pycurry.dbc module.

Copyright (c) 2008 Fons Dijkstra

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""

import pycurry.dbc as sut
sut.level.set(sut.level.max())

import os
import re
import inspect
import unittest
import threading

import pycurry as pyc
import pycurry.err as err
import pycurry.tst as tst


class level(unittest.TestCase):

    def setUp(self):
        self.__lvl = os.getenv(sut.level.PYCURRY_DBC_LEVEL)
        if self.__lvl is not None:
            del os.environ[sut.level.PYCURRY_DBC_LEVEL]

    def tearDown(self):
        if self.__lvl is None and sut.level.PYCURRY_DBC_LEVEL in os.environ:
            del os.environ[sut.level.PYCURRY_DBC_LEVEL]
        else:
            os.environ[sut.level.PYCURRY_DBC_LEVEL] = self.__lvl

    def test_check(self):
        sut.level.check(None)
        sut.level.check(sut.level.require)
        sut.level.check(sut.level.ensure)
        sut.level.check(sut.level.invariant)
        sut.level.check(sut.level.require.upper())
        sut.level.check(sut.level.ensure.upper())
        sut.level.check(sut.level.invariant.upper())
        self.failUnlessRaises(ValueError, sut.level.check, False)
        self.failUnlessRaises(ValueError, sut.level.check, "None")
        self.failUnlessRaises(ValueError, sut.level.check, "poep")

    def test_max(self):
        self.failUnlessEqual(sut.level.max(), sut.level.invariant)

    def test_get(self):
        self.failUnlessEqual(sut.level.get(), sut.level.require)
        os.environ[sut.level.PYCURRY_DBC_LEVEL] = str(None)
        self.failUnlessEqual(sut.level.get(), None)
        os.environ[sut.level.PYCURRY_DBC_LEVEL] = sut.level.require
        self.failUnlessEqual(sut.level.get(), sut.level.require)
        os.environ[sut.level.PYCURRY_DBC_LEVEL] = sut.level.ensure
        self.failUnlessEqual(sut.level.get(), sut.level.ensure)
        os.environ[sut.level.PYCURRY_DBC_LEVEL] = sut.level.invariant
        self.failUnlessEqual(sut.level.get(), sut.level.invariant)
        os.environ[sut.level.PYCURRY_DBC_LEVEL]= "poep"
        self.failUnlessRaises(ValueError, sut.level.get)

    def test_set(self):
        self.failUnlessEqual(sut.level.set(), sut.level.require)
        self.failUnlessEqual(sut.level.set(None), sut.level.require)
        self.failUnlessEqual(sut.level.set(sut.level.require), None)
        self.failUnlessEqual(sut.level.set(sut.level.ensure), sut.level.require)
        self.failUnlessEqual(
                sut.level.set(sut.level.invariant), sut.level.ensure)
        self.failUnlessRaises(ValueError, sut.level.set, "poep")
        self.failUnlessEqual(sut.level.get(), sut.level.invariant)

    def test_init(self):
        sut.level()
        sut.level(None)
        sut.level(sut.level.require)
        sut.level(sut.level.ensure)
        sut.level(sut.level.invariant)
        self.failUnlessRaises(ValueError, sut.level, "poep")

    def test_repr(self):
        repr(sut.level())

    def test_str(self):
        str(sut.level())

    def test_hash(self):
        hash(sut.level())

    def test_eq(self):
        self.failUnless(sut.level() == sut.level())
        self.failUnless(sut.level(None) == sut.level(None))
        self.failIf(sut.level() == sut.level(None))
        self.failIf(sut.level() == sut.level.require)

    def test_lt(self):
        self.failUnless(sut.level(None) < \
                        sut.level(sut.level.require) < \
                        sut.level(sut.level.ensure) < \
                        sut.level(sut.level.invariant))
        self.failIf(sut.level(sut.level.invariant) <
                sut.level(sut.level.invariant))
        self.failUnlessRaises(TypeError, sut.level(None).__lt__, None)

    def test_le(self):
        self.failUnless(sut.level() <= sut.level())

    def test_ne(self):
        self.failIf(sut.level() != sut.level())

    def test_gt(self):
        self.failIf(sut.level() > sut.level())

    def test_ge(self):
        self.failUnless(sut.level() >= sut.level())

    def test_with(self):
        self.failUnlessEqual(sut.level.get(), sut.level.require)
        with sut.level(None):
            self.failUnlessEqual(sut.level.get(), None)
        self.failUnlessEqual(sut.level.get(), sut.level.require)


class tls_condition(unittest.TestCase):

    def setUp(self):
        self.__sut = sut.tls_condition()

    def test_1(self):
        with self.__sut as test:
            self.failUnless(test)

    def test_n(self):
        with self.__sut as test:
            self.failUnless(test)
            with self.__sut as test:
                self.failIf(test)
            with self.__sut as test:
                self.failIf(test)
                with self.__sut as test:
                    self.failIf(test)
        with self.__sut as test:
            self.failUnless(test)

    def test_cur(self):
        with self.__sut as test:
            self.failUnless(test)
            thd = threading.Thread(
                    name = pyc.fully_qualified_name(self.test_cur),
                    target = err.unhandled_exception_handler.handle,
                    args = [self.test_n])
            thd.start()
            thd.join()


class tls_object(unittest.TestCase):

    def setUp(self):
        self.__sut = sut.tls_object()

    def test_1(self):
        with self.__sut.use(self) as test:
            self.failUnless(test)

    def test_n(self):
        with self.__sut.use(self) as test:
            self.failUnless(test)
            with self.__sut.use(self) as test:
                self.failIf(test)
            with self.__sut.use(self) as test:
                self.failIf(test)
                with self.__sut.use(self) as test:
                    self.failIf(test)
        with self.__sut.use(self) as test:
            self.failUnless(test)

    def test_1_m(self):
        with self.__sut.use(self) as test:
            self.failUnless(test)
        with self.__sut.use(self.__sut) as test:
            self.failUnless(test)

    def test_n_m(self):
        with self.__sut.use(self) as test:
            self.failUnless(test)
            with self.__sut.use(self.__sut) as test:
                self.failUnless(test)
                with self.__sut.use(self) as test:
                    self.failIf(test)

    def test_cur(self):
        with self.__sut.use(self) as test:
            self.failUnless(test)
            with self.__sut.use(self.__sut) as test:
                self.failUnless(test)
                thd = threading.Thread(
                        name = pyc.fully_qualified_name(self.test_cur),
                        target = err.unhandled_exception_handler.handle,
                        args = [self.test_n_m])
                thd.start()
                thd.join()


class cls_defined(object):
    def defined(self):
        pass

class cls_none(object):
    def override(self):
        pass

class cls_empty(cls_none):
    """"""
    def but_override(self):
        """"""
        pass

class cls_a(cls_empty):
    """
    invariant: __inv
    """

    def __new__(self):
        """
        require: pre_a
        ensure: __post
        """
        pass

    def __init__(self):
        """
        require: pre_a
        ensure: __post
        """
        pass

    def __del__(self):
        """
        require: pre_a
        ensure: __post
        """
        pass

    def __private(self):
        """
        require: __pre
        ensure: __post
        """
        pass

    def public(self):
        """
        require: __pre
        ensure: __return__
        """
        pass

    def override(self):
        """
        require_else: pre_a
        ensure_then: __post
        """
        pass

    def but_override(self):
        """
        require: pre_a
        ensure: __post
        """
        pass

    def no_override(self):
        """
        require_else: pre_a
        ensure_then: __post
        """
        pass

    def foo(self):
        """
        require: pre_a
        """
        pass

class cls_b(cls_a):
    """
    invariant: __inv
    """

    def __init__(self):
        """
        require_else: pre_b
        ensure_then: __post
        """
        pass

    def __private(self):
        """
        require: __pre
        ensure: __post
        """
        pass

    def override(self):
        """
        require_else: pre_b
        ensure_then: __post
        """
        pass

    def foo(self):
        pass

class cls_c(cls_b):

    def __init__(self):
        """
        require: pre_c
        ensure: __post
        """
        pass

    def foo(self):
        """
        require_else: pre_c
        """
        pass

class cls_d(cls_c):
    def override(self):
        pass

    def foo(self):
        pass

def func_defined():
    pass

def func_none():
    pass

def func_empty():
    """"""
    pass

def func_contract():
    """
    require: pre
    ensure: __return__
    """
    pass

def func_override():
    """
    require_else: pre
    ensure_then: post
    """
    pass

def func_mangled():
    """
    require: __pre
    ensure: __post
    """
    pass

def func_locals(a, b = 0):
    pass

class scan(unittest.TestCase):

    def __compile(self, cond):
        if cond is None:
            return (None, None)
        return (cond, compile(cond, "<string>", "eval"))

    def test_cls_defined_inv(self):
        sut.dbc_class.scan_inv(cls_defined)
        self.failUnlessRaises(ValueError, sut.dbc_class.scan_inv,
                cls_defined)

    def test_cls_defined_pre(self):
        sut.dbc_class.scan_pre(cls_defined.defined, cls_defined)
        self.failUnlessRaises(ValueError, sut.dbc_class.scan_pre,
                cls_defined.defined, cls_defined)

    def test_cls_defined_post(self):
        sut.dbc_class.scan_post(cls_defined.defined, cls_defined)
        self.failUnlessRaises(ValueError, sut.dbc_class.scan_post,
                cls_defined.defined, cls_defined)

    def test_func_defined_pre(self):
        sut.dbc_class.scan_pre(func_defined)
        self.failUnlessRaises(ValueError, sut.dbc_class.scan_pre,
                func_defined)

    def test_func_defined_post(self):
        sut.dbc_class.scan_post(func_defined)
        self.failUnlessRaises(ValueError, sut.dbc_class.scan_post,
                func_defined)

    def test_cls_none_inv(self):
        sut.dbc_class.scan_inv(cls_none)
        self.failUnlessEqual(cls_none.__inv__, [])

    def test_cls_empty_inv(self):
        sut.dbc_class.scan_inv(cls_empty)
        self.failUnlessEqual(cls_empty.__inv__, [])

    def test_cls_a_inv(self):
        sut.dbc_class.scan_inv(cls_a)
        self.failUnlessEqual(cls_a.__inv__, [
            self.__compile("_cls_a__inv")])

    def test_cls_b_inv(self):
        sut.dbc_class.scan_inv(cls_b)
        self.failUnlessEqual(cls_b.__inv__, [
            self.__compile("_cls_a__inv"),
            self.__compile("_cls_b__inv")])

    def test_cls_c_inv(self):
        sut.dbc_class.scan_inv(cls_c)
        self.failUnlessEqual(cls_c.__inv__, [
            self.__compile("_cls_a__inv"),
            self.__compile("_cls_b__inv")])

    def test_cls_none_override_pre(self):
        sut.dbc_class.scan_pre(cls_none.override, cls_none)
        self.failUnlessEqual(cls_none.override.__pre__, [])

    def test_cls_empty_but_override_pre(self):
        sut.dbc_class.scan_pre(cls_empty.but_override, cls_empty)
        self.failUnlessEqual(cls_empty.but_override.__pre__, [])

    def test_cls_a_new_pre(self):
        self.failUnlessRaises(SyntaxError, sut.dbc_class.scan_pre,
            cls_a.__new__, cls_a)

    def test_cls_a_del_pre(self):
        self.failUnlessRaises(SyntaxError, sut.dbc_class.scan_pre,
            cls_a.__del__, cls_a)

    def test_cls_a_init_pre(self):
        sut.dbc_class.scan_pre(cls_a.__init__, cls_a)
        self.failUnlessEqual(cls_a.__init__.__pre__, [
            self.__compile("pre_a")])

    def test_cls_a_private_pre(self):
        sut.dbc_class.scan_pre(cls_a._cls_a__private, cls_a)
        self.failUnlessEqual(cls_a._cls_a__private.__pre__, [
            self.__compile("_cls_a__pre")])

    def test_cls_a_public_pre(self):
        self.failUnlessRaises(SyntaxError, sut.dbc_class.scan_pre,
                cls_a.public, cls_a)

    def test_cls_a_override_pre(self):
        sut.dbc_class.scan_pre(cls_a.override, cls_a)
        self.failUnlessEqual(cls_a.override.__pre__, [
            (None, None),
            self.__compile("pre_a")])

    def test_cls_a_but_override_pre(self):
        self.failUnlessRaises(SyntaxError, sut.dbc_class.scan_pre,
                cls_a.but_override, cls_a)

    def test_cls_a_no_override_pre(self):
        self.failUnlessRaises(SyntaxError, sut.dbc_class.scan_pre,
                cls_a.no_override, cls_a)

    def test_cls_b_init_pre(self):
        self.failUnlessRaises(SyntaxError, sut.dbc_class.scan_pre,
                cls_b.__init__, cls_b)

    def test_cls_b_private_pre(self):
        sut.dbc_class.scan_pre(cls_b._cls_b__private, cls_b)
        self.failUnlessEqual(cls_b._cls_b__private.__pre__, [
            self.__compile("_cls_b__pre")])

    def test_cls_b_override_pre(self):
        sut.dbc_class.scan_pre(cls_b.override, cls_b)
        self.failUnlessEqual(cls_b.override.__pre__, [
            self.__compile(None),
            self.__compile("pre_a"),
            self.__compile(None),
            self.__compile("pre_b")])

    def test_cls_c_init_pre(self):
        sut.dbc_class.scan_pre(cls_c.__init__, cls_c)
        self.failUnlessEqual(cls_c.__init__.__pre__, [
            self.__compile("pre_c")])

    def test_cls_d_override_pre(self):
        sut.dbc_class.scan_pre(cls_d.override, cls_d)
        self.failUnlessEqual(cls_d.override.__pre__, [
            self.__compile(None),
            self.__compile("pre_a"),
            self.__compile(None),
            self.__compile("pre_b")])

    def test_cls_a_foo_pre(self):
        sut.dbc_class.scan_pre(cls_a.foo, cls_a)
        self.failUnlessEqual(cls_a.foo.__pre__, [
            self.__compile("pre_a")])

    def test_cls_b_foo_pre(self):
        sut.dbc_class.scan_pre(cls_b.foo, cls_b)
        self.failUnlessEqual(cls_b.foo.__pre__, [
            self.__compile("pre_a")])

    def test_cls_c_foo_pre(self):
        sut.dbc_class.scan_pre(cls_c.foo, cls_c)
        self.failUnlessEqual(cls_c.foo.__pre__, [
            self.__compile("pre_a"),
            self.__compile(None),
            self.__compile("pre_c")])

    def test_cls_d_foo_pre(self):
        sut.dbc_class.scan_pre(cls_d.foo, cls_d)
        self.failUnlessEqual(cls_d.foo.__pre__, [
            self.__compile("pre_a"),
            self.__compile(None),
            self.__compile("pre_c")])

    def test_func_none_pre(self):
        sut.dbc_class.scan_pre(func_none)
        self.failUnlessEqual(func_none.__pre__, [])

    def test_func_empty_pre(self):
        sut.dbc_class.scan_pre(func_empty)
        self.failUnlessEqual(func_empty.__pre__, [])

    def test_func_contract_pre(self):
        sut.dbc_class.scan_pre(func_contract)
        self.failUnlessEqual(func_contract.__pre__, [
            self.__compile("pre")])

    def test_func_override_post(self):
        self.failUnlessRaises(SyntaxError, sut.dbc_class.scan_pre,
                func_override)

    def test_func_mangled_pre(self):
        sut.dbc_class.scan_pre(func_mangled)
        self.failUnlessEqual(func_mangled.__pre__, [
            self.__compile("__pre")])

    def test_cls_none_override_post(self):
        sut.dbc_class.scan_post(cls_none.override, cls_none)
        self.failUnlessEqual(cls_none.override.__post__, [])

    def test_cls_empty_but_override_post(self):
        sut.dbc_class.scan_post(cls_empty.but_override, cls_empty)
        self.failUnlessEqual(cls_empty.but_override.__post__, [])

    def test_cls_a_new_post(self):
        self.failUnlessRaises(SyntaxError, sut.dbc_class.scan_post,
                cls_a.__new__, cls_a)

    def test_cls_a_del_post(self):
        self.failUnlessRaises(SyntaxError, sut.dbc_class.scan_post,
                cls_a.__del__, cls_a)

    def test_cls_a_init_post(self):
        sut.dbc_class.scan_post(cls_a.__init__, cls_a)
        self.failUnlessEqual(cls_a.__init__.__post__, [
            self.__compile("_cls_a__post")])

    def test_cls_a_private_post(self):
        sut.dbc_class.scan_post(cls_a._cls_a__private, cls_a)
        self.failUnlessEqual(cls_a._cls_a__private.__post__, [
            self.__compile("_cls_a__post")])

    def test_cls_a_public_post(self):
        sut.dbc_class.scan_post(cls_a.public, cls_a)
        self.failUnlessEqual(cls_a.public.__post__, [
            self.__compile("__return__")])

    def test_cls_a_override_post(self):
        sut.dbc_class.scan_post(cls_a.override, cls_a)
        self.failUnlessEqual(cls_a.override.__post__, [
            self.__compile("_cls_a__post")])

    def test_cls_a_but_override_post(self):
        self.failUnlessRaises(SyntaxError, sut.dbc_class.scan_post,
                cls_a.but_override, cls_a)

    def test_cls_a_no_override_post(self):
        self.failUnlessRaises(SyntaxError, sut.dbc_class.scan_post,
                cls_a.no_override, cls_a)

    def test_cls_b_init_post(self):
        self.failUnlessRaises(SyntaxError, sut.dbc_class.scan_post,
                cls_b.__init__, cls_b)

    def test_cls_b_private_post(self):
        sut.dbc_class.scan_post(cls_b._cls_b__private, cls_b)
        self.failUnlessEqual(cls_b._cls_b__private.__post__, [
            self.__compile("_cls_b__post")])

    def test_cls_b_override_post(self):
        sut.dbc_class.scan_post(cls_b.override, cls_b)
        self.failUnlessEqual(cls_b.override.__post__, [
            self.__compile("_cls_a__post"),
            self.__compile("_cls_b__post")])

    def test_cls_c_init_post(self):
        sut.dbc_class.scan_post(cls_c.__init__, cls_c)
        self.failUnlessEqual(cls_c.__init__.__post__, [
            self.__compile("_cls_c__post")])

    def test_cls_d_override(self):
        sut.dbc_class.scan_post(cls_d.override, cls_d)
        self.failUnlessEqual(cls_d.override.__post__, [
            self.__compile("_cls_a__post"),
            self.__compile("_cls_b__post")])

    def test_func_none_post(self):
        sut.dbc_class.scan_post(func_none)
        self.failUnlessEqual(func_none.__post__, [])

    def test_func_empty_post(self):
        sut.dbc_class.scan_post(func_empty)
        self.failUnlessEqual(func_empty.__post__, [])

    def test_func_contract_post(self):
        sut.dbc_class.scan_post(func_contract)
        self.failUnlessEqual(func_contract.__post__, [
            self.__compile("__return__")])

    def test_func_override_post(self):
        self.failUnlessRaises(SyntaxError, sut.dbc_class.scan_post,
                func_override)

    def test_func_mangled_post(self):
        sut.dbc_class.scan_post(func_mangled)
        self.failUnlessEqual(func_mangled.__post__, [
            self.__compile("__post")])

    def test_scan_func_locals(self):
        spec = inspect.getargspec(func_locals)
        self.failUnlessEqual(sut.dbc_class.scan_locals(
            func_locals, spec, 1), {"a": 1, "b": 0})
        self.failUnlessEqual(sut.dbc_class.scan_locals(
            func_locals, spec, 1, 2), {"a": 1, "b": 2})
        self.failUnlessEqual(sut.dbc_class.scan_locals(
            func_locals, spec, a = 1), {"a": 1, "b": 0})
        self.failUnlessEqual(sut.dbc_class.scan_locals(
            func_locals, spec, a = 1, b = 2), {"a": 1, "b": 2})
        self.failUnlessRaises(TypeError, sut.dbc_class.scan_locals,
                func_locals, spec)
        self.failUnlessRaises(TypeError, sut.dbc_class.scan_locals,
                func_locals, spec, 1, 2, 3)
        self.failUnlessRaises(TypeError, sut.dbc_class.scan_locals,
                func_locals, spec, c = 3)


class parse(unittest.TestCase):

    def test_object_inv(self):
        sut.dbc_class.parse_inv({}, object.__str__, object)

    def test_cls_none_inv(self):
        sut.dbc_class.parse_inv({}, cls_none.override, cls_none)

    def test_cls_d_inv(self):
        sut.dbc_class.parse_inv(
                {"_cls_a__inv": True, "_cls_b__inv": True},
                cls_d.override, cls_d)
        self.failUnlessRaises(
                sut.class_invariant_exception, sut.dbc_class.parse_inv,
                {"_cls_a__inv": True, "_cls_b__inv": False},
                cls_d.override, cls_d)
        self.failUnlessRaises(
                sut.class_invariant_exception, sut.dbc_class.parse_inv,
                {"_cls_a__inv": False, "_cls_b__inv": True},
                cls_d.override, cls_d)
        self.failUnlessRaises(
                sut.class_invariant_exception, sut.dbc_class.parse_inv,
                {"_cls_a__inv": False, "_cls_b__inv": False},
                cls_d.override, cls_d)

    def test_object_post(self):
        sut.dbc_class.parse_post({}, None, object.__str__, object)

    def test_cls_none_override_post(self):
        sut.dbc_class.parse_post({}, None, cls_none.override, cls_none)

    def test_cls_a_public_post(self):
        sut.dbc_class.parse_post({}, True, cls_a.public, cls_a)
        self.failUnlessRaises(
                sut.postcondition_exception, sut.dbc_class.parse_post,
                {}, False, cls_a.public, cls_a)

    def test_cls_d_override_post(self):
        sut.dbc_class.parse_post(
                {"_cls_a__post": True, "_cls_b__post": True}, None,
                cls_d.override, cls_d)
        self.failUnlessRaises(
                sut.postcondition_exception, sut.dbc_class.parse_post,
                {"_cls_a__post": True, "_cls_b__post": False}, None,
                cls_d.override, cls_d)
        self.failUnlessRaises(
                sut.postcondition_exception, sut.dbc_class.parse_post,
                {"_cls_a__post": False, "_cls_b__post": True}, None,
                cls_d.override, cls_d)
        self.failUnlessRaises(
                sut.postcondition_exception, sut.dbc_class.parse_post,
                {"_cls_a__post": False, "_cls_b__post": False}, None,
                cls_d.override, cls_d)

    def test_str_post(self):
        sut.dbc_class.parse_post({}, None, str)

    def test_func_none_post(self):
        sut.dbc_class.parse_post({}, None, func_none)

    def test_func_contract_post(self):
        sut.dbc_class.parse_post({}, True, func_contract)
        self.failUnlessRaises(
                sut.postcondition_exception, sut.dbc_class.parse_post,
                {}, False, func_contract)

    def test_object_pre(self):
        sut.dbc_class.parse_pre({}, object.__str__, object)

    def test_cls_none_override_pre(self):
        sut.dbc_class.parse_pre({}, cls_none.override, cls_none)

    def test_cls_d_override_pre(self):
        sut.dbc_class.parse_pre(
                {"pre_a": True, "pre_b": True}, cls_d.override, cls_d)
        sut.dbc_class.parse_pre(
                {"pre_a": True, "pre_b": False}, cls_d.override, cls_d)
        sut.dbc_class.parse_pre(
                {"pre_a": False, "pre_b": True}, cls_d.override, cls_d)
        sut.dbc_class.parse_pre(
                {"pre_a": False, "pre_b": False}, cls_d.override, cls_d)

    def test_cls_a_foo_pre(self):
        sut.dbc_class.parse_pre(
                {"pre_a": True}, cls_a.foo, cls_a)
        self.failUnlessRaises(
                sut.precondition_exception, sut.dbc_class.parse_pre,
                {"pre_a": False}, cls_a.foo, cls_a)

    def test_cls_b_foo_pre(self):
        sut.dbc_class.parse_pre(
                {"pre_a": True}, cls_b.foo, cls_b)
        self.failUnlessRaises(
                sut.precondition_exception, sut.dbc_class.parse_pre,
                {"pre_a": False}, cls_b.foo, cls_b)

    def test_cls_c_foo_pre(self):
        sut.dbc_class.parse_pre(
                {"pre_a": True, "pre_c": True}, cls_c.foo, cls_c)
        sut.dbc_class.parse_pre(
                {"pre_a": True, "pre_c": False}, cls_c.foo, cls_c)
        sut.dbc_class.parse_pre(
                {"pre_a": False, "pre_c": True}, cls_c.foo, cls_c)
        self.failUnlessRaises(
                sut.precondition_exception, sut.dbc_class.parse_pre,
                {"pre_a": False, "pre_c": False}, cls_c.foo, cls_c)

    def test_cls_d_foo_pre(self):
        sut.dbc_class.parse_pre(
                {"pre_a": True, "pre_c": True}, cls_d.foo, cls_d)
        sut.dbc_class.parse_pre(
                {"pre_a": True, "pre_c": False}, cls_d.foo, cls_d)
        sut.dbc_class.parse_pre(
                {"pre_a": False, "pre_c": True}, cls_d.foo, cls_d)
        self.failUnlessRaises(
                sut.precondition_exception, sut.dbc_class.parse_pre,
                {"pre_a": False, "pre_c": False}, cls_d.foo, cls_d)

    def test_str_pre(self):
        sut.dbc_class.parse_pre({}, str)

    def test_func_none_pre(self):
        sut.dbc_class.parse_pre({}, func_none)

    def test_func_contract_pre(self):
        sut.dbc_class.parse_pre({"pre": True}, func_contract)
        self.failUnlessRaises(
                sut.precondition_exception, sut.dbc_class.parse_pre,
                {"pre": False}, func_contract)


class dbc_class(unittest.TestCase):

    def test_structor(self):
        import pycurry.test.xyz as xyz
        xyz.structor()

    def test_none(self):
        import pycurry.test.xyz as xyz
        xyz.none().foo()

    def test_require(self):
        import pycurry.test.xyz as xyz
        xyz.require().foo()
        self.failUnlessRaises(sut.precondition_exception,
                xyz.require().foo, False)

    def test_ensure(self):
        import pycurry.test.xyz as xyz
        xyz.ensure().foo()
        self.failUnlessRaises(sut.precondition_exception,
                xyz.ensure().foo, pre = False)
        self.failUnlessRaises(sut.postcondition_exception,
                xyz.ensure().foo, post = False)

    def test_invariant(self):
        import pycurry.test.xyz as xyz
        xyz.invariant().foo()
        self.failUnlessRaises(sut.precondition_exception,
                xyz.invariant().foo, pre = False)
        self.failUnlessRaises(sut.postcondition_exception,
                xyz.invariant().foo, post = False)
        self.failUnlessRaises(sut.class_invariant_exception,
                xyz.invariant, False)


class doc(object):
    """This class contains class-invariants:

    invariant: True
    invariant: True and \
            self.__inv
    invariant: True

    That's it!
    """

    __metaclass__ = sut.dbc_class

    def __init__(self):
        super(doc, self).__init__()
        self.__inv = True

    def none(self):
        """This method contains no DbC.
        """
        pass

    def require(self, pre):
        """This method contains only preconditions:

        require: True
        require: True and \
                pre
        require: True

        That's it!
        """
        pass

    def ensure(self, post):
        """This methods contains only postconditions:

        ensure: True
        ensure: True and \
                post
        ensure: True
        ensure: self.__inv

        That's it!
        """
        pass

    def invariant(self, inv):
        self.__inv = inv


class doc_test(unittest.TestCase):

    def setUp(self):
        self.__impl = doc()

    def tearDown(self):
        self.__impl = doc()

    def test_none(self):
        self.__impl.none()

    def test_require(self):
        self.__impl.require(True)
        try:
            self.__impl.require(False)
        except sut.precondition_exception as e:
            str(e)
            self.failUnless(e.client.endswith("test_require"))
            self.failUnless(e.supplier.endswith("doc.require"))
            self.failUnless(e.condition == "True and pre")
        else:
            self.fail("sut.precondition_exception not raised")

    def test_ensure(self):
        self.__impl.ensure(True)
        try:
            self.__impl.ensure(False)
        except sut.postcondition_exception as e:
            str(e)
            self.failUnless(e.client.endswith("test_ensure"))
            self.failUnless(e.supplier.endswith("doc.ensure"))
            self.failUnless(e.condition == "True and post")
        else:
            self.fail("sut.postcondition_exception not raised")

    def test_invariant(self):
        self.__impl.invariant(True)
        try:
            self.__impl.invariant(False)
        except sut.class_invariant_exception as e:
            str(e)
            self.failUnless(e.client.endswith("test_invariant"))
            self.failUnless(e.supplier.endswith("doc.invariant"))
            self.failUnless(e.condition == "True and self._doc__inv")
        else:
            self.fail("sut.class_invariant_exception not raised")


class access(object):

    __metaclass__ = sut.dbc_class

    def public(self, pre = True, post = True):
        """
        require: pre
        ensure: post
        """
        pass

    def _protected(self, pre = True, post = True):
        """
        require: pre
        ensure: post
        """
        pass

    def __private(self, pre = True, post = True):
        """
        require: pre
        ensure: post
        """
        pass

    def __internal__(self, pre = True, post = True):
        """
        require: pre
        ensure: post
        """
        pass


class access_test(unittest.TestCase):

    def setUp(self):
        self.__impl = access()

    def tearDown(self):
        self.__impl = None

    def test_public(self):
        self.failUnlessRaises(sut.precondition_exception,
                self.__impl.public, pre = False)
        self.failUnlessRaises(sut.postcondition_exception,
                self.__impl.public, post = False)

    def test_protected(self):
        self.failUnlessRaises(sut.precondition_exception,
                self.__impl._protected, pre = False)
        self.failUnlessRaises(sut.postcondition_exception,
                self.__impl._protected, post = False)

    def test_private(self):
        self.failUnlessRaises(sut.precondition_exception,
                self.__impl._access__private, pre = False)
        self.failUnlessRaises(sut.postcondition_exception,
                self.__impl._access__private, post = False)

    def test_internal(self):
        self.failUnlessRaises(sut.precondition_exception,
                self.__impl.__internal__, pre = False)
        self.failUnlessRaises(sut.postcondition_exception,
                self.__impl.__internal__, post = False)


class nested(object):
    """
    invariant: self.query()
    invariant: self.__inv
    """

    __metaclass__ = sut.dbc_class

    def __init__(self):
        super(nested, self).__init__()
        self.__inv = True

    def query(self, pre = False, post = False):
        """
        require: pre
        ensure: post
        """
        return True

    def command(self, inv = True):
        """
        require: self.query()
        ensure: self.query()
        """
        self.__inv = inv
        self.query(True, True)
        self.__inv = True


class nested_test(unittest.TestCase):

    def test0(self):
        nested().command()

    def test1(self):
        nested().command(False)


class interface(object):

    __metaclass__ = sut.dbc_class

    def foo(self,
            int_pre = True,
            int_post = True,
            abs_pre = True,
            abs_post = True,
            con_pre = True,
            con_post = True):
        """
        require: int_pre
        ensure: int_post
        """
        pass


class abstract_class(interface):
    """
    invariant: self.__inv
    """

    def __init__(self,
            abs_pre = True,
            abs_post = True,
            abs_inv = True):
        """
        require: abs_pre
        ensure: abs_post
        """
        super(abstract_class, self).__init__()
        self.__inv = abs_inv

    def foo(self,
            int_pre = True,
            int_post = True,
            abs_pre = True,
            abs_post = True,
            con_pre = True,
            con_post = True):
        """
        require_else: abs_pre
        ensure_then: abs_post
        """
        pass

    def fop(self, inv = True):
        self._concrete_class__inv = inv


class concrete_class(abstract_class):
    """
    invariant: self.__inv
    """

    def __init__(self,
            abs_pre = True,
            abs_post = True,
            abs_inv = True,
            con_pre = True,
            con_post = True,
            con_inv = True,
            con_abs_inv = True):
        """
        require: con_pre
        ensure: con_post
        """
        super(concrete_class, self).__init__(abs_pre, abs_post, abs_inv)
        self.__inv = con_inv
        self._abstract_class__inv = con_abs_inv

    def foo(self,
            int_pre = True,
            int_post = True,
            abs_pre = True,
            abs_post = True,
            con_pre = True,
            con_post = True):
        """
        require_else: con_pre
        ensure_then: con_post
        """
        pass

    def foq(self, inv = True):
        self._abstract_class__inv = inv


class inheritance_test(unittest.TestCase):

    def test_lifetime0(self):
        concrete_class()

    def test_lifetime1(self):
        try:
            concrete_class(abs_pre = False)
        except sut.precondition_exception as e:
            self.failUnless(e.client.endswith("__init__"))
            self.failUnless(e.supplier.endswith("abstract_class.__init__"))
            self.failUnless(e.condition == "abs_pre")
        else:
            self.fail("sut.precondition_exception not raised")

    def test_lifetime2(self):
        try:
            concrete_class(abs_post = False)
        except sut.postcondition_exception as e:
            self.failUnless(e.client.endswith("__init__"))
            self.failUnless(e.supplier.endswith("abstract_class.__init__"))
            self.failUnless(e.condition == "abs_post")
        else:
            self.fail("sut.postcondition_exception not raised")

    def test_lifetime3(self):
        try:
            concrete_class(abs_inv = False)
        except sut.class_invariant_exception as e:
            self.failUnless(e.client.endswith("__init__"))
            self.failUnless(e.supplier.endswith("abstract_class.__init__"))
            self.failUnless(e.condition == "self._abstract_class__inv")
        else:
            self.fail("sut.class_invariant_exception not raised")

    def test_lifetime4(self):
        try:
            concrete_class(con_pre = False)
        except sut.precondition_exception as e:
            self.failUnless(e.client.endswith("test_lifetime4"))
            self.failUnless(e.supplier.endswith("concrete_class.__init__"))
            self.failUnless(e.condition == "con_pre")
        else:
            self.fail("sut.precondition_exception not raised")

    def test_lifetime5(self):
        try:
            concrete_class(con_post = False)
        except sut.postcondition_exception as e:
            self.failUnless(e.client.endswith("test_lifetime5"))
            self.failUnless(e.supplier.endswith("concrete_class.__init__"))
            self.failUnless(e.condition == "con_post")
        else:
            self.fail("sut.postcondition_exception not raised")

    def test_lifetime6(self):
        try:
            concrete_class(con_inv = False)
        except sut.class_invariant_exception as e:
            self.failUnless(e.client.endswith("test_lifetime6"))
            self.failUnless(e.supplier.endswith("concrete_class.__init__"))
            self.failUnless(e.condition == "self._concrete_class__inv")
        else:
            self.fail("sut.class_invariant_exception not raised")

    def test_lifetime7(self):
        try:
            concrete_class(con_abs_inv = False)
        except sut.class_invariant_exception as e:
            self.failUnless(e.client.endswith("test_lifetime7"))
            self.failUnless(e.supplier.endswith("concrete_class.__init__"))
            self.failUnless(e.condition == "self._abstract_class__inv")
        else:
            self.fail("sut.class_invariant_exception not raised")

    def test_foo0(self):
        concrete_class().foo()

    def test_foo1(self):
        concrete_class().foo(int_pre = False)

    def test_foo2(self):
        try:
            concrete_class().foo(int_post = False)
        except sut.postcondition_exception as e:
            self.failUnless(e.client.endswith("test_foo2"))
            self.failUnless(e.supplier.endswith("concrete_class.foo"))
            self.failUnless(e.condition == "int_post")
        else:
            self.fail("sut.postcondition_exception not raised")

    def test_foo3(self):
        concrete_class().foo(abs_pre = False)

    def test_foo4(self):
        try:
            concrete_class().foo(abs_post = False)
        except sut.postcondition_exception as e:
            self.failUnless(e.client.endswith("test_foo4"))
            self.failUnless(e.supplier.endswith("concrete_class.foo"))
            self.failUnless(e.condition == "abs_post")
        else:
            self.fail("sut.postcondition_exception not raised")

    def test_foo5(self):
        concrete_class().foo(con_pre = False)

    def test_foo6(self):
        try:
            concrete_class().foo(con_post = False)
        except sut.postcondition_exception as e:
            self.failUnless(e.client.endswith("test_foo6"))
            self.failUnless(e.supplier.endswith("concrete_class.foo"))
            self.failUnless(e.condition == "con_post")
        else:
            self.fail("sut.postcondition_exception not raised")

    def test_foo7(self):
        concrete_class().foo(int_pre = False, abs_pre = False)

    def test_foo8(self):
        concrete_class().foo(int_pre = False, con_pre = False)

    def test_foo9(self):
        concrete_class().foo(abs_pre = False, con_pre = False)

    def test_foo10(self):
        try:
            concrete_class().foo(
                    int_pre = False, abs_pre = False, con_pre = False)
        except sut.precondition_exception as e:
            self.failUnless(e.client.endswith("test_foo10"))
            self.failUnless(e.supplier.endswith("concrete_class.foo"))
            self.failUnless(e.condition == "con_pre")
        else:
            self.fail("sut.precondition_exception not raised")

    def test_foo11(self):
        try:
            concrete_class().foo(int_post = False, abs_post = False)
        except sut.postcondition_exception as e:
            self.failUnless(e.client.endswith("test_foo11"))
            self.failUnless(e.supplier.endswith("concrete_class.foo"))
            self.failUnless(e.condition == "int_post")
        else:
            self.fail("sut.postcondition_exception not raised")

    def test_foo12(self):
        try:
            concrete_class().foo(int_post = False, con_post = False)
        except sut.postcondition_exception as e:
            self.failUnless(e.client.endswith("test_foo12"))
            self.failUnless(e.supplier.endswith("concrete_class.foo"))
            self.failUnless(e.condition == "int_post")
        else:
            self.fail("sut.postcondition_exception not raised")

    def test_foo13(self):
        try:
            concrete_class().foo(abs_post = False, con_post = False)
        except sut.postcondition_exception as e:
            self.failUnless(e.client.endswith("test_foo13"))
            self.failUnless(e.supplier.endswith("concrete_class.foo"))
            self.failUnless(e.condition == "abs_post")
        else:
            self.fail("sut.postcondition_exception not raised")

    def test_foo14(self):
        try:
            concrete_class().foo(
                    int_post = False, abs_post = False, con_post = False)
        except sut.postcondition_exception as e:
            self.failUnless(e.client.endswith("test_foo14"))
            self.failUnless(e.supplier.endswith("concrete_class.foo"))
            self.failUnless(e.condition == "int_post")
        else:
            self.fail("sut.postcondition_exception not raised")

    def test_fop0(self):
        concrete_class().fop()

    def test_fop1(self):
        try:
            concrete_class().fop(False)
        except sut.class_invariant_exception as e:
            self.failUnless(e.client.endswith("test_fop1"))
            self.failUnless(e.supplier.endswith("concrete_class.fop"))
            self.failUnless(e.condition == "self._concrete_class__inv")
        else:
            self.fail("sut.class_invariant_exception not raised")

    def test_foq0(self):
        concrete_class().foq()

    def test_foq1(self):
        try:
            concrete_class().foq(False)
        except sut.class_invariant_exception as e:
            self.failUnless(e.client.endswith("test_foq1"))
            self.failUnless(e.supplier.endswith("concrete_class.foq"))
            self.failUnless(e.condition == "self._abstract_class__inv")
        else:
            self.fail("sut.class_invariant_exception not raised")


class a_level(object):
    __metaclass__ = sut.dbc_class

sut.level.set(None)
class none_level(a_level):
    """
    invariant: False
    """

    def __init__(self):
        """
        require: False
        ensure: False
        """
        pass

    def foo(self):
        """
        require: False
        ensure: False
        """
        pass


sut.level.set(sut.level.require)
class req_level(a_level):
    """
    invariant: False
    """

    def __init__(self, pre = True):
        """
        require: pre
        ensure: False
        """
        pass

    def foo(self, pre = True):
        """
        require: pre
        ensure: False
        """
        pass


sut.level.set(sut.level.ensure)
class ens_level(a_level):
    """
    invariant: False
    """

    def __init__(self, post = True):
        """
        require: True
        ensure: post
        """
        pass

    def foo(self, post = True):
        """
        require: True
        ensure: post
        """
        pass


sut.level.set(sut.level.invariant)
class inv_level(a_level):
    """
    invariant: self.__inv
    """

    def __init__(self, inv = True):
        """
        require: True
        ensure: True
        """
        self.__inv = inv

    def foo(self, inv = True):
        """
        require: True
        ensure: True
        """
        self.__inv = inv


class levels_test(unittest.TestCase):

    def test_none(self):
        none_level().foo()

    def test_req0(self):
        req_level().foo()

    def test_req1(self):
        self.failUnlessRaises(sut.precondition_exception,
                req_level, False)

    def test_req2(self):
        self.failUnlessRaises(sut.precondition_exception,
                req_level().foo, False)

    def test_ens0(self):
        ens_level().foo()

    def test_ens1(self):
        self.failUnlessRaises(sut.postcondition_exception,
                ens_level, False)

    def test_ens2(self):
        self.failUnlessRaises(sut.postcondition_exception,
                ens_level().foo, False)

    def test_inv0(self):
        inv_level().foo()

    def test_inv1(self):
        self.failUnlessRaises(sut.class_invariant_exception,
                inv_level, False)

    def test_inv2(self):
        self.failUnlessRaises(sut.class_invariant_exception,
                inv_level().foo, False)


class misc(object):
    """
    invariant: self.__inv
    """

    __metaclass__ = sut.dbc_class

    def __init__(self, inv = True):
        self.__inv = False
        self.foo(None)
        self.__inv = inv

    def foo(self, param, expr = True):
        pass


class misc_test(unittest.TestCase):

    def test_method_from_constructor(self):
        misc()
        try:
            misc(inv = False)
        except sut.class_invariant_exception as e:
            self.failUnless(e.client.endswith("test_method_from_constructor"))
            self.failUnless(e.supplier.endswith("misc.__init__"))
            self.failUnless(e.condition == "self._misc__inv")
        else:
            self.fail("sut.class_invariant_exception not raised")


class dbc_function(unittest.TestCase):

    def test_none(self):
        with sut.level(None):
            @sut.dbc_function
            def foo(pre = True, result = True):
                """
                require: pre
                ensure: __return__
                """
                return result
            self.failUnless(foo() is True)
            self.failUnless(foo(pre = False) is True)
            self.failUnless(foo(result = False) is False)

    def test_require(self):
        with sut.level(sut.level.require):
            @sut.dbc_function
            def foo(pre = True, result = True):
                """
                require: pre
                ensure: __return__
                """
                return result
            self.failUnless(foo() is True)
            self.failUnlessRaises(sut.precondition_exception,
                    foo, pre = False)
            self.failUnless(foo(result = False) is False)

    def test_ensure(self):
        with sut.level(sut.level.ensure):
            @sut.dbc_function
            def foo(pre = True, result = True):
                """
                require: pre
                ensure: __return__
                """
                return result
            self.failUnless(foo() is True)
            self.failUnlessRaises(sut.precondition_exception,
                    foo, pre = False)
            self.failUnlessRaises(sut.postcondition_exception,
                    foo, result = False)

    def test_exception(self):
        @sut.dbc_function
        def foo(pre = True, result = False):
            """
            require: pre
            ensure: __return__
            """
            return result
        try:
            foo(pre = False)
        except sut.precondition_exception as e:
            self.failUnless(e.client.endswith("test_exception"))
            self.failUnless(e.supplier.endswith("foo"))
            self.failUnless(e.condition == "pre")
        else:
            self.fail("precondition_exception not raised")
        try:
            foo(result = False)
        except sut.postcondition_exception as e:
            self.failUnless(e.client.endswith("test_exception"))
            self.failUnless(e.supplier.endswith("foo"))
            self.failUnless(e.condition == "__return__")
        else:
            self.fail("postcondition_exception not raised")


class predicates(unittest.TestCase):

    def test_exists(self):
        self.failUnless(sut.exists([]) is False)
        self.failUnless(sut.exists([False]) is False)
        self.failUnless(sut.exists([True]) is True)
        self.failUnless(sut.exists([1, 2], lambda x: x == 0) is False)
        self.failUnless(sut.exists([1, 2], lambda x: x == 1) is True)
        self.failUnless(sut.exists([1, 2], lambda x, y: x == y, 1) is True)
        self.failUnless(sut.exists([1, 2], lambda x, y: x == y, y = 1) is True)

    def test_forall(self):
        self.failUnless(sut.forall([]) is True)
        self.failUnless(sut.forall([False]) is False)
        self.failUnless(sut.forall([True]) is True)
        self.failUnless(sut.forall([1, 2], lambda x: x > 1) is False)
        self.failUnless(sut.forall([1, 2], lambda x: x > 0) is True)
        self.failUnless(sut.forall([1, 2], lambda x, y: x > y, 0) is True)
        self.failUnless(sut.forall([1, 2], lambda x, y: x > y, y = 0) is True)


def suite():
    return unittest.TestSuite([
        unittest.TestLoader().loadTestsFromTestCase(level),
        unittest.TestLoader().loadTestsFromTestCase(tls_object),
        unittest.TestLoader().loadTestsFromTestCase(tls_condition),
        unittest.TestLoader().loadTestsFromTestCase(scan),
        unittest.TestLoader().loadTestsFromTestCase(parse),
        unittest.TestLoader().loadTestsFromTestCase(dbc_class),
        unittest.TestLoader().loadTestsFromTestCase(dbc_function),
        unittest.TestLoader().loadTestsFromTestCase(predicates),
        unittest.TestLoader().loadTestsFromTestCase(doc_test),
        unittest.TestLoader().loadTestsFromTestCase(access_test),
        unittest.TestLoader().loadTestsFromTestCase(nested_test),
        unittest.TestLoader().loadTestsFromTestCase(inheritance_test),
        unittest.TestLoader().loadTestsFromTestCase(levels_test),
        unittest.TestLoader().loadTestsFromTestCase(misc_test),
    ])

if __name__ == "__main__":
    tst.main(suite(), [sut])

