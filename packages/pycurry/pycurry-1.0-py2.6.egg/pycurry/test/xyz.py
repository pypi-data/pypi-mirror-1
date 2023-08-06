"""Todo.

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


class structor(object):

    __metaclass__ = dbc.dbc_class

    def __new__(cls):
        return super(structor, cls).__new__(cls)

    def __del__(cls):
        pass


with dbc.level(None):
    class none(object):
        """
        invariant: False
        """

        __metaclass__ = dbc.dbc_class

        def foo(self):
            """
            require: False
            ensure: False
            """
            pass


with dbc.level(dbc.level.require):
    class require(object):
        """
        invariant: False
        """

        __metaclass__ = dbc.dbc_class

        def foo(self, pre = True):
            """
            require: pre
            ensure: False
            """
            pass


with dbc.level(dbc.level.ensure):
    class ensure(object):
        """
        invariant: False
        """

        __metaclass__ = dbc.dbc_class

        def foo(self, pre = True, post = True):
            """
            require: pre
            ensure: post
            """
            pass


with dbc.level(dbc.level.invariant):
    class invariant(object):
        """
        invariant: self.inv
        """

        __metaclass__ = dbc.dbc_class

        def __init__(self, inv = True):
            self.inv = inv

        def foo(self, pre = True, post = True):
            """
            require: pre
            ensure: post
            """
            pass

