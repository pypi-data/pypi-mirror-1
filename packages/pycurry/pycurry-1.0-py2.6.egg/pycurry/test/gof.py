"""Tests for the gof module.

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

import pycurry.tst as tst
import pycurry.gof as sut


class composite(unittest.TestCase):

    def setUp(self):
        self.__sut = sut.composite()

    def test_repr(self):
        repr(self.__sut)

    def test_str(self):
        str(self.__sut)

    def test_parent(self):
        self.failUnless(self.__sut.parent is None)

    def test_capacity(self):
        self.failUnlessEqual(self.__sut.capacity, sys.maxint)

    def test_len(self):
        self.failUnlessEqual(len(self.__sut), 0)

    def test_in(self):
        self.failIf(self.__sut in self.__sut)

    def test_iter(self):
        for child in self.__sut:
            self.fail("sut has no children")

    def test_root(self):
        self.failUnless(self.__sut.root)

    def test_empty(self):
        self.failUnless(self.__sut.empty)

    def test_full(self):
        self.failIf(self.__sut.full)

    def test_add(self):
        self.__sut.add(sut.leaf())

    def test_remove(self):
        child = sut.composite()
        self.__sut.add(child)
        self.__sut.remove(child)


class leaf(unittest.TestCase):

    def setUp(self):
        self.__sut = sut.leaf()

    def test_repr(self):
        repr(self.__sut)

    def test_str(self):
        str(self.__sut)

    def test_parent(self):
        self.failUnless(self.__sut.parent is None)

    def test_capacity(self):
        self.failUnlessEqual(self.__sut.capacity, 0)

    def test_len(self):
        self.failUnlessEqual(len(self.__sut), 0)

    def test_in(self):
        self.failIf(self.__sut in self.__sut)

    def test_iter(self):
        for child in self.__sut:
            self.fail("sut has no children")

    def test_root(self):
        self.failUnless(self.__sut.root)

    def test_empty(self):
        self.failUnless(self.__sut.empty)

    def test_full(self):
        self.failUnless(self.__sut.full)


class config(unittest.TestCase):

    def test_leaf_attrs(self):
        leaf = sut.leaf(attrs = {"a": NotImplemented})
        self.failUnless(leaf.a is NotImplemented)
        leaf.a = None
        self.failUnless(leaf.a is None)

    def test_comp_attrs(self):
        comp = sut.composite(attrs = {"a": NotImplemented})
        self.failUnless(comp.a is NotImplemented)
        comp.a = None
        self.failUnless(comp.a is None)

    def test_comp_set(self):
        comp = sut.composite(container = set)
        leaf = sut.leaf()
        comp.add(leaf)
        comp.remove(leaf)

    def test_comp_list(self):
        comp = sut.composite(container = list)
        leaf = sut.leaf()
        comp.add(leaf)
        comp.remove(leaf)


class usage(unittest.TestCase):

    def setUp(self):
        self.__root = sut.composite(attrs = {"name": "root"})
        self.__elem = sut.composite(
                attrs = {"name": "elem"}, container = list)
        self.__a = sut.leaf(attrs = {"name": "a"})
        self.__b = sut.leaf(attrs = {"name": "b"})
        self.__c = sut.leaf(attrs = {"name": "c"})
        self.__root.add(self.__elem)
        self.__elem.add(self.__a)
        self.__elem.add(self.__b)
        self.__root.add(self.__c)

    def _test(self):
        pass # TODO


def suite():
    return unittest.TestSuite([
        unittest.TestLoader().loadTestsFromTestCase(composite),
        unittest.TestLoader().loadTestsFromTestCase(leaf),
        unittest.TestLoader().loadTestsFromTestCase(config),
        unittest.TestLoader().loadTestsFromTestCase(usage),
    ])

if __name__ == "__main__":
    tst.main(suite(), [sut])

