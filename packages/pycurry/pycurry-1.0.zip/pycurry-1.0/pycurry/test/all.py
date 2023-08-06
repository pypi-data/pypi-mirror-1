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

import unittest
import pycurry.test
import pycurry.test.dbc
import pycurry.test.log
import pycurry.test.err
import pycurry.test.thd
import pycurry.test.tst
import pycurry.test.gof


def suite():
    return unittest.TestSuite([pycurry.test.suite(),
                               pycurry.test.dbc.suite(),
                               pycurry.test.log.suite(),
                               pycurry.test.err.suite(),
                               pycurry.test.thd.suite(),
                               pycurry.test.tst.suite(),
                               pycurry.test.gof.suite()])

