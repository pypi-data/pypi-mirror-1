"""Tests for the pycurry.err module.

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

import pycurry.dbc as dbc
dbc.level.set(dbc.level.max())

import os
import re
import sys
import logging
import unittest
import threading

import pycurry as pyc
import pycurry.tst as tst
import pycurry.err as sut


class exception_handler(unittest.TestCase):

    info = re.compile(
r'''^Unhandled exception in thread MainThread\(None\):
Traceback \(most recent call last\):
  File ".*%s", line \d+, in test_\w+
    assert None
AssertionError(\\n)?
$''' %(os.path.join("pycurry", "test", "err.py").replace("\\", "\\\\")),
    re.MULTILINE)

    def setUp(self):
        self.__sut = sut.exception_handler()

    def test_format_thd(self):
        self.failUnlessEqual(sut.exception_handler.format_thd(
            threading.currentThread()),
            "Unhandled exception in thread MainThread(None):\n")

    def test_format(self):
        try:
            assert None
        except:
            self.failUnless(self.info.match(
                sut.exception_handler.format(
                    threading.currentThread(), *sys.exc_info())))
    
    def test_handle(self):
        try:
            assert None
        except:
            self.failUnlessRaises(NotImplementedError, self.__sut.handle,
                threading.currentThread(), *sys.exc_info())


class print_exception_handler(unittest.TestCase):

    def write(self, msg):
        self.__buf += msg

    def setUp(self):
        self.__sut = sut.print_exception_handler(self)
        self.__buf = "" # the buffer to log to

    def test_handle(self):
        try:
            assert None
        except:
            self.__sut.handle(threading.currentThread(), *sys.exc_info())
            self.failUnless(exception_handler.info.match(self.__buf))


class log_exception_handler(unittest.TestCase):

    def write(self, msg):
        self.__buf += msg

    def flush(self):
        pass

    def setUp(self):
        self.__sut = sut.log_exception_handler()
        self.__buf = "" # the buffer to log to
        # get the logger used by the sut
        self.__log = logging.getLogger(
                pyc.fully_qualified_name(sut.log_exception_handler))
        self.__log.setLevel(logging.DEBUG) # check for all possible logging
        # create the stream handler writing to the buffer
        self.__han = logging.StreamHandler(self)
        self.__log.addHandler(self.__han)

    def tearDown(self):
        self.__log.removeHandler(self.__han)
        
    def test_handle(self):
        try:
            assert None
        except:
            self.__sut.handle(threading.currentThread(), *sys.exc_info())
            self.failUnless(exception_handler.info.match(self.__buf))


class gmail_exception_handler(unittest.TestCase):

    def setUp(self):
        self.__sut = sut.gmail_exception_handler(
                user = "pycurry.test",
                password = "?geheim!",
                addrs = "pycurry.test@gmail.com")

    def test_handle(self):
        try:
            assert None
        except:
            self.__sut.handle(threading.currentThread(), *sys.exc_info())


class pdb_exception_handler(unittest.TestCase):

    def setUp(self):
        self.__sut = sut.pdb_exception_handler()

    def test_handle(self):
        try:
            assert True # set to None to test-by-hand
        except:
            self.__sut.handle(threading.currentThread(), *sys.exc_info())


class winpdb_exception_handler(unittest.TestCase):

    def setUp(self):
        self.__sut = sut.winpdb_exception_handler()

    def test_handle(self):
        try:
            assert True # set to None to test-by-hand
        except:
            self.__sut.handle(threading.currentThread(), *sys.exc_info())


class unittest_exception_handler(unittest.TestCase):

    def setUp(self):
        self.__res = unittest.TestResult()
        self.__sut = sut.unittest_exception_handler(self.__res)

    def test_handle(self):
        try:
            assert None
        except:
            self.failUnless(self.__res.wasSuccessful())
            self.__sut.handle(threading.currentThread(), *sys.exc_info())
            self.failUnless(not self.__res.wasSuccessful())


class exit_exception_handler(unittest.TestCase):

    def setUp(self):
        self.__sut = sut.exit_exception_handler()

    def test_handle(self):
        try:
            assert None
        except:
            self.failUnlessRaises(SystemExit, self.__sut.handle,
                    threading.currentThread(), *sys.exc_info())


class unhandled_exception_handler(unittest.TestCase, sut.exception_handler):

    def handle(self, exc_thd, exc_type, exc_value, exc_traceback):
        self.__handled = True

    def system(self, exc_type, exc_value, exc_traceback):
        self.__system = True

    def __proxy(self, call, *args, **kwargs):
        call(*args, **kwargs)

    def __call(self, expr = False):
        assert expr

    def setUp(self):
        self.__handled = False
        self.__system = False
        sut.unhandled_exception_handler.set_proxy(None)
        sut.unhandled_exception_handler.clear_handlers()

    def tearDown(self):
        sut.unhandled_exception_handler.set_proxy(None)
        sut.unhandled_exception_handler.clear_handlers()

    def test_init(self):
        self.failUnlessRaises(dbc.precondition_exception,
                sut.unhandled_exception_handler)

    def test_set_proxy(self):
        sut.unhandled_exception_handler.set_proxy(self.__proxy)

    def test_has_handler(self):
        self.failIf(sut.unhandled_exception_handler.has_handler(
            sut.exception_handler()))

    def test_prepend_handler(self):
        sut.unhandled_exception_handler.prepend_handler(
                sut.exception_handler())

    def test_append_handler(self):
        sut.unhandled_exception_handler.append_handler(
                sut.exception_handler())

    def test_remove_handler(self):
        handler = sut.exception_handler()
        sut.unhandled_exception_handler.append_handler(handler)
        sut.unhandled_exception_handler.remove_handler(handler)

    def test_handle_no_exception(self):
        # direct access to avoid coverage problems ...
        sut.unhandled_exception_handler. \
                _unhandled_exception_handler__handlers.append(self)
        sut.unhandled_exception_handler.handle(self.__call, True)
        self.failIf(self.__handled)

    def test_handle_exception(self):
        # direct access to avoid coverage problems ...
        sut.unhandled_exception_handler. \
                _unhandled_exception_handler__handlers.append(self)
        sut.unhandled_exception_handler.handle(self.__call)
        self.failUnless(self.__handled)

    def test_handle_proxy(self):
        # direct access to avoid coverage problems ...
        sut.unhandled_exception_handler. \
                _unhandled_exception_handler__handlers.append(self)
        sut.unhandled_exception_handler.set_proxy(self.__proxy)
        sut.unhandled_exception_handler.handle(self.__call)
        self.failUnless(self.__handled)

    def test_handle_system(self):
        sys.__excepthook__ = self.system
        sut.unhandled_exception_handler.handle(self.__call)
        self.failUnless(self.__system)

    def _test_debug(self): # enable to test-by-hand
        sut.unhandled_exception_handler.append_handler(
                sut.print_exception_handler())
        sut.unhandled_exception_handler.append_handler(
                sut.pdb_exception_handler())
        sut.unhandled_exception_handler.append_handler(
                sut.exit_exception_handler())
        self.failUnlessRaises(SystemExit,
                sut.unhandled_exception_handler.handle, self.__call)

    def _test_release(self): # enable to test-by-hand
        sut.unhandled_exception_handler.append_handler(
                sut.log_exception_handler())
        sut.unhandled_exception_handler.append_handler(
                sut.gmail_exception_handler(
                    user = "pycurry.test",
                    password = "?geheim!",
                    addrs = "pycurry.test@gmail.com"))
        sut.unhandled_exception_handler.append_handler(
                sut.exit_exception_handler())
        self.failUnlessRaises(SystemExit,
                sut.unhandled_exception_handler.handle, self.__call)

    def _test_unittest(self): # enable to test-by-hand
        thd = threading.Thread(target = sut.han.handle, args = (self.__main, ))
        thd.start()
        thd.join()


def suite():
    return unittest.TestSuite([
        unittest.TestLoader().loadTestsFromTestCase(exception_handler),
        unittest.TestLoader().loadTestsFromTestCase(print_exception_handler),
        unittest.TestLoader().loadTestsFromTestCase(log_exception_handler),
        unittest.TestLoader().loadTestsFromTestCase(gmail_exception_handler),
        unittest.TestLoader().loadTestsFromTestCase(pdb_exception_handler),
        unittest.TestLoader().loadTestsFromTestCase(winpdb_exception_handler),
        unittest.TestLoader().loadTestsFromTestCase(unittest_exception_handler),
        unittest.TestLoader().loadTestsFromTestCase(exit_exception_handler),
        unittest.TestLoader().loadTestsFromTestCase(unhandled_exception_handler)
    ])

if __name__ == "__main__":
    tst.main(suite(), [sut])

