"""Tests for the pycurry module.

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

import re
import os
import sys
import unittest

import pycurry as sut
import pycurry.tst as tst


class pass_(unittest.TestCase):

    def test(self):
        self.failUnless(sut.pass_() is None)


class fully_qualified_name(unittest.TestCase):

    def test_module(self):
        self.failUnlessEqual(sut.fully_qualified_name(unittest),
                "unittest")

    def test_function(self):
        self.failUnlessEqual(sut.fully_qualified_name(unittest._strclass),
                "unittest._strclass")

    def test_function_class(self):
        self.failUnlessEqual(sut.fully_qualified_name(
            unittest._strclass, unittest.TestCase),
                "unittest.TestCase._strclass")

    def test_class(self):
        self.failUnlessEqual(sut.fully_qualified_name(unittest.TestCase),
                "unittest.TestCase")

    def test_method(self):
        self.failUnlessEqual(sut.fully_qualified_name(unittest.TestCase.run),
                "unittest.TestCase.run")

    def test_unknown(self):
        self.failUnlessRaises(TypeError, sut.fully_qualified_name, None)


class source_filename(unittest.TestCase):

    def test_py(self):
        self.failUnlessEqual(sut.source_filename("test.py"), "test.py")

    def test_pyc(self):
        self.failUnlessEqual(sut.source_filename("test.pyc"), "test.py")

    def test_pyo(self):
        self.failUnlessEqual(sut.source_filename("test.pyo"), "test.py")

    def test_txt(self):
        self.failUnless(sut.source_filename("test.txt") is None)


class resolve_filename(unittest.TestCase):

    def setUp(self):
        self.__name = os.path.join("pycurry", "test", "__init__.py")

    def test_resolve_filename_relative(self):
        self.failUnless(sut.resolve_filename(self.__name) is not None)

    def test_resolve_filename_relative_unknown(self):
        self.failUnless(sut.resolve_filename("poep") is None)

    def test_resolve_filename_absolute(self):
        self.failUnless(sut.resolve_filename(sys.executable) is not None)

    def test_resolve_filename_absolute_unknown(self):
        self.failUnless(sut.resolve_filename(
            os.path.join(os.getcwd(), "poep")) is None)


class empty(object):

    def __init__(self):
        super(empty, self).__init__()

    def foo(self):
        pass

class single(empty):

    def __init__(self):
        super(single, self).__init__()
        self.__impl = 0

class multiple(single):

    def __init__(self):
        super(multiple, self).__init__()
        self.__impl = "null"


class generic_repr(unittest.TestCase):

    def test_empty(self):
        self.failUnless(re.match(
            "^<class '(pycurry\.test|__main__)\.empty'>: \{\}$",
            sut.generic_repr(empty())) is not None)

    def test_single(self):
        self.failUnless(re.match(
            "^<class '(pycurry\.test|__main__)\.single'>: " +
            "\{'_single__impl': 0\}$",
            sut.generic_repr(single())) is not None)

    def test_multiple(self):
        self.failUnless(re.match(
            "^<class '(pycurry\.test|__main__)\.multiple'>: " +
            "\{'_multiple__impl': 'null', '_single__impl': 0\}$",
            sut.generic_repr(multiple())) is not None)
    
    def test_no_object(self):
        self.failUnlessRaises(TypeError, sut.generic_repr, None)


class generic_str(unittest.TestCase):

    def test_empty(self):
        self.failUnless(re.match(
            "^empty\(0x[0-9A-F]{8}\)",
            sut.generic_str(empty())) is not None)

    def test_single(self):
        self.failUnless(re.match(
            "^single\(0x[0-9A-F]{8}\): impl=0$",
            sut.generic_str(single())) is not None)

    def test_multiple(self):
        self.failUnless(re.match(
            "^multiple\(0x[0-9A-F]{8}\): impl=null; impl=0$",
            sut.generic_str(multiple())) is not None)

    def test_no_object(self):
        self.failUnlessRaises(TypeError, sut.generic_str, None)


def suite():
    return unittest.TestSuite([
        unittest.TestLoader().loadTestsFromTestCase(pass_),
        unittest.TestLoader().loadTestsFromTestCase(fully_qualified_name),
        unittest.TestLoader().loadTestsFromTestCase(source_filename),
        unittest.TestLoader().loadTestsFromTestCase(resolve_filename),
        unittest.TestLoader().loadTestsFromTestCase(generic_repr),
        unittest.TestLoader().loadTestsFromTestCase(generic_str),
    ])

if __name__ == "__main__":
    tst.main(suite(), [sut])

