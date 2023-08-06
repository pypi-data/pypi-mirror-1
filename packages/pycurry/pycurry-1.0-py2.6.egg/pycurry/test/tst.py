"""Tests for the pycurry.tst module.

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

import sys
import unittest

import pycurry.tst as sut


class pylint(unittest.TestCase):

    def write(self, msg):
        pass

    def setUp(self):
        self.__old = sys.stdout
        sys.stdout = self

    def tearDown(self):
        sys.stdout = self.__old

    def test_str(self):
        sut.pylint("pycurry.test.tst")

    def test_mod(self):
        sut.pylint(__import__(__name__))


class text_test_runner(unittest.TestCase):

    def setUp(self):
        self.__sut = sut.text_test_runner()

    def test_result(self):
        self.failUnless(self.__sut.result is self.__sut.result)

    def test_makeResult(self):
        self.failUnless(self.__sut._makeResult() is self.__sut._makeResult())

    def test_result_makeResult(self):
        self.failUnless(self.__sut.result is self.__sut._makeResult())


class coverage(unittest.TestCase):

    def write(self, msg):
        pass

    def setUp(self):
        self.__sut = sut.coverage([__import__(__name__)], self)

    def test(self):
        pass

    def _test_with(self): # enable to test without --coverage
        with self.__sut:
            pass


class profiler(unittest.TestCase):

    def write(self, msg):
        pass

    def __call(self):
        pass

    def setUp(self):
        sut.profiler.init((sut, __import__(__name__)),
                (sut.profiler.calls,
                 sut.profiler.callers,
                 sut.profiler.callees),
                sut.profiler.calls,
                self)

    def test_init(self):
        self.failUnlessRaises(dbc.precondition_exception, sut.profiler)

    def test_profile(self):
        sut.profiler.profile(self.__call)


def suite():
    return unittest.TestSuite([
        unittest.TestLoader().loadTestsFromTestCase(pylint),
        unittest.TestLoader().loadTestsFromTestCase(text_test_runner),
        unittest.TestLoader().loadTestsFromTestCase(coverage),
        unittest.TestLoader().loadTestsFromTestCase(profiler),
    ])

if __name__ == "__main__":
    sut.main(suite(), [sut])
 
