"""Tests for the pycurry.thd module.

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

import time
import warnings
import unittest
import threading

import pycurry as pyc
import pycurry.err as err
import pycurry.tst as tst
import pycurry.thd as sut


class unsync(unittest.TestCase):

    def __test(self, sync):
        with sync:
            with sut.unsync(sync):
                pass

    def test_lock(self):
        self.__test(threading.Lock())

    def test_rlock(self):
        self.__test(threading.RLock())

    def test_cond(self):
        self.__test(threading.Condition())


class action(unittest.TestCase):

    def __call(self, p1, p2, p3 = 3):
        self.__p1 = p1
        self.__p2 = p2
        self.__p3 = p3

    def __query(self):
        return False

    def setUp(self):
        self.__p1 = self.__p2 = self.__p3 = None
        self.__sut = sut.action(self.__call, 1, p2 = 2)

    def test_str(self):
        self.failUnlessEqual(str(self.__sut),
                "%s((1,), {'p2': 2})" %(self.__call))

    def test_call(self):
        self.failUnless(self.__sut() is None)
        self.failUnlessEqual(self.__p1, 1)
        self.failUnlessEqual(self.__p2, 2)
        self.failUnlessEqual(self.__p3, 3)

    def test_warning(self):
        with warnings.catch_warnings():
            warnings.simplefilter("error", RuntimeWarning)
            try:
                self.failUnless(sut.action(self.__query)() is None)
            except RuntimeWarning as e:
                self.failUnlessEqual(e.args[0], "discarded %s: False" %(
                    pyc.fully_qualified_name(self.__query)))
            else:
                self.fail("RuntimeWarning not raised")


class future(unittest.TestCase):

    def __call(self, p1, p2, p3 = 3):
        self.__p1 = p1
        self.__p2 = p2
        self.__p3 = p3
        return 4

    def __res(self):
        self.failUnlessEqual(self.__sut.get_result(), 4)

    def setUp(self):
        self.__p1 = self.__p2 = self.__p3 = None
        self.__sut = sut.future(self.__call, 1, p2 = 2)

    def test_str(self):
        self.failUnlessEqual(str(self.__sut),
                "%s((1,), {'p2': 2})" %(self.__call))

    def test_call(self):
        self.failUnless(self.__sut() is None)
        self.failUnlessEqual(self.__p1, 1)
        self.failUnlessEqual(self.__p2, 2)
        self.failUnlessEqual(self.__p3, 3)

    def test_is_called(self):
        self.failIf(self.__sut.is_called())
        self.__sut()
        self.failUnless(self.__sut.is_called())

    def test_get_result(self):
        self.__sut()
        self.__res()

    def test_get_result_async(self):
        thd = threading.Thread(
                name = pyc.fully_qualified_name(self.__res),
                target = err.unhandled_exception_handler.handle,
                args = [self.__res])
        thd.start()
        time.sleep(0)
        self.__sut()
        thd.join()


class active_object(unittest.TestCase):

    def __call(self):
        pass

    def setUp(self):
        self.__sut = sut.active_object(pyc.fully_qualified_name(type(self)))

    def tearDown(self):
        self.__sut.stop(True)
        
    def test_repr(self):
        repr(self.__sut)

    def test_str(self):
        str(self.__sut)

    def test_is_stopped(self):
        self.failIf(self.__sut.is_stopped())

    def test_stop(self):
        self.__sut.stop()

    def test_schedule(self):
        time.sleep(0)
        self.__sut.schedule(self.__call)

    def test_schedule_action(self):
        time.sleep(0)
        self.__sut.schedule(sut.action(self.__call))

    def test_schedule_future(self):
        time.sleep(0)
        self.failUnless(self.__sut.schedule(
            sut.future(self.__call)).get_result() is None)


def suite():
    return unittest.TestSuite([
        unittest.TestLoader().loadTestsFromTestCase(unsync),
        unittest.TestLoader().loadTestsFromTestCase(action),
        unittest.TestLoader().loadTestsFromTestCase(future),
        unittest.TestLoader().loadTestsFromTestCase(active_object),
    ])

if __name__ == "__main__":
    tst.main(suite(), [sut])

