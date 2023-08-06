"""Tests for the pycurry.log module.

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

import re
import logging
import logging.config
import unittest

import pycurry as pyc
import pycurry.tst as tst
import pycurry.log as sut


class TestHandler(logging.StreamHandler):

    def __init__(self, impl):
        logging.StreamHandler.__init__(self, impl)
        self.__impl = impl

    def doRollover(self):
        self.__impl.doRollover()


class rotating_memory_handler(unittest.TestCase):

    regex = re.compile("^test: (.+)\\n$")

    def write(self, msg):
        match = self.regex.match(msg);
        self.failUnless(match is not None)
        self.__buf.append(match.group(1))

    def flush(self):
        self.__flushed = True

    def doRollover(self):
        self.__rolled_over = True

    def __test(self, buf, flushed, rolled_over):
        self.failUnlessEqual(self.__buf, buf)
        self.failUnlessEqual(self.__flushed, flushed)
        self.failUnlessEqual(self.__rolled_over, rolled_over)
        self.__buf = []
        self.__flushed = False
        self.__rolled_over = False

    def setUp(self):
        self.__buf = []
        self.__flushed = False
        self.__rolled_over = False
        self.__sut = sut.rotating_memory_handler(
                3, logging.WARNING, TestHandler, self)
        self.__sut.setFormatter(logging.Formatter("test: %(message)s"))
        self.__log = logging.getLogger(pyc.fully_qualified_name(type(self)))
        self.__log.setLevel(logging.DEBUG)
        self.__log.addHandler(self.__sut)

    def tearDown(self):
        self.__sut.flush()
        self.__log.removeHandler(self.__sut)
        self.__test([], True, False)

    def test_repr(self):
        repr(self.__sut)

    def test_str(self):
        str(self.__sut)

    def test_log_normal(self):
        self.__log.info("1")
        self.__log.info("2")
        self.__log.info("3")
        self.__log.info("4")
        self.__log.info("5")
        self.__test([], False, False)

    def test_log_error_no_history(self):
        self.__log.error("e")
        self.__test(["e"], True, True)

    def test_log_error_history_not_full(self):
        self.__log.info("1")
        self.__log.error("e")
        self.__test(["1", "e"], True, True)

    def test_log_error_history_full(self):
        self.__log.info("1")
        self.__log.info("2")
        self.__log.info("3")
        self.__log.error("e")
        self.__test(["2", "3", "e"], True, True)

    def test_log_error_error(self):
        self.__log.info("1")
        self.__log.error("e")
        self.__test(["1", "e"], True, True)
        self.__log.info("2")
        self.__log.error("e")
        self.__test(["2", "e"], True, True)


def suite():
    return unittest.TestSuite([
        unittest.TestLoader().loadTestsFromTestCase(rotating_memory_handler),
    ])

if __name__ == "__main__":
    tst.main(suite(), [sut])

