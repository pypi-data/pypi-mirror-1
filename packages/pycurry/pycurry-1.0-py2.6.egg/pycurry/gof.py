"""Implements design patterns from the GoF book.

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

import sys
import collections

import pycurry as pyc
import pycurry.dbc as dbc


class component(object):
    """
    invariant: isinstance(self, collections.Sized)
    invariant: isinstance(self, collections.Iterable)
    invariant: isinstance(self, collections.Container)
    invariant: 0 <= self.capacity <= sys.maxint
    invariant: 0 <= len(self) <= self.capacity
    invariant: None not in self
    invariant: self.parent is None or self in self.parent
    invariant: not [child for child in self if not child.parent is self]
    invariant: (self.parent is None) == self.root
    invariant: (len(self) == 0) == self.empty
    invariant: (len(self) == self.capacity) == self.full
    """

    __metaclass__ = dbc.dbc_class

    def __set_parent(self, parent):
        """
        require: parent is None or isinstance(parent, composite)
        ensure: self.__parent is parent
        """
        self.__parent = parent

    def __init__(self, attrs = None):
        """
        require: attrs is None or isinstance(attrs, collections.Mapping)
        require: attrs is None or \
                not [key for key in attrs.keys() if not isinstance(key, str)]
        ensure: self.root
        ensure: self.empty
        ensure: attrs is None or \
                not [(key, value) for (key, value) in attrs.items() \
                    if not getattr(self, key) is value]
        """
        super(component, self).__init__()
        self.__parent = None
        if attrs is not None:
            for key, value in attrs.items():
                setattr(self, key, value)

    def __repr__(self):
        """
        ensure_then: isinstance(__return__, str)
        """
        return pyc.generic_repr(self)

    def __str__(self):
        """
        ensure_then: isinstance(__return__, str)
        """
        return pyc.generic_str(self)

    @property
    def parent(self):
        """
        ensure: __return__ is None or isinstance(__return__, composite)
        """
        return self.__parent

    @property
    def capacity(self):
        """
        ensure: isinstance(__return__, int)
        """
        raise NotImplementedError

    def __len__(self):
        """
        ensure: isinstance(__return__, int)
        """
        raise NotImplementedError

    def __contains__(self, child):
        """
        require: isinstance(child, component)
        ensure: isinstance(__return__, bool)
        """
        raise NotImplementedError

    def __iter__(self):
        """
        ensure: isinstance(__return__, collections.Iterator)
        """
        raise NotImplementedError

    @property
    def root(self):
        """
        ensure: isinstance(__return__, bool)
        """
        return self.parent is None

    @property
    def empty(self):
        """
        ensure: isinstance(__return__, bool)
        """
        return len(self) == 0

    @property
    def full(self):
        """
        ensure: isinstance(__return__, bool)
        """
        return len(self) == self.capacity

    def add(self, child):
        """
        require: isinstance(child, component)
        require: child is not self
        require: child.root
        require: not self.full
        require: child not in self
        ensure: child in self
        ensure: not self.empty
        """
        raise NotImplementedError

    def remove(self, child):
        """
        require: isinstance(child, component)
        require: child in self
        ensure: child not in self
        ensure: not self.full
        """
        raise NotImplementedError


class composite(component):
    """
    invariant: self.capacity > 0
    """

    def __init__(self, attrs = None, container = set, capacity = sys.maxint):
        """
        require: isinstance(container(), collections.MutableSet) or \
                 isinstance(container(), collections.MutableSequence)
        require: isinstance(capacity, int)
        require: 0 < capacity <= sys.maxint
        ensure: self.capacity == capacity
        """
        self.__capacity = capacity
        self.__children = container()
        super(composite, self).__init__(attrs)
        if isinstance(self.__children, collections.MutableSet):
            self.__add = self.__children.add
            self.__remove = self.__children.remove
        else:
            self.__add = self.__children.append # pylint: disable-msg=E1101
            self.__remove = self.__children.remove

    @property
    def capacity(self):
        return self.__capacity

    def __len__(self):
        return len(self.__children)

    def __contains__(self, child):
        return child in self.__children

    def __iter__(self):
        return iter(self.__children)

    def add(self, child):
        self.__add(child)
        child._component__set_parent(self) # pylint: disable-msg=W0212

    def remove(self, child):
        child._component__set_parent(None) # pylint: disable-msg=W0212
        self.__remove(child)


class leaf(component):
    """
    invariant: self.capacity == 0
    """

    def __init__(self, attrs = None):
        super(leaf, self).__init__(attrs)

    @property
    def capacity(self):
        return 0

    def __len__(self):
        return 0

    def __contains__(self, child):
        """
        ensure_then: not __return__
        """
        return False

    def __iter__(self):
        return iter(())

    def add(self, child):
        assert None, "not allowed on leafs"

    def remove(self, child):
        assert None, "not allowed on leafs"

