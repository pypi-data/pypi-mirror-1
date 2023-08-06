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

import logging
import warnings
import threading
import contextlib
import collections

import pycurry as pyc
import pycurry.err as err
import pycurry.dbc as dbc


@contextlib.contextmanager
def unsync(sync):
    """Unsynchronizes a formally synchronized object. The provided
    synchronized object must be a threading.Lock, threading.RLock or
    threading.Condition object. Re-entered acquires are taken into account,
    that is the synchronized object will always be unsynchronized.
    """
    # enter
    if hasattr(sync, "_release_save"):
        # pylint: disable-msg=W0212
        state = sync._release_save()
    else:
        sync.release()
    # block
    try:
        yield # nothing to return
    finally:
        # exit
        if hasattr(sync, "_acquire_restore"):
            # pylint: disable-msg=W0212
            sync._acquire_restore(state)
        else:
            sync.acquire()


class action(object):
    """Todo.
    """

    __metaclass__ = dbc.dbc_class

    def __init__(self, call, *args, **kwargs):
        """
        require: isinstance(call, collections.Callable)
        """
        super(action, self).__init__()
        self.__call = call
        self.__args = args
        self.__kwargs = kwargs

    def __str__(self):
        """
        ensure_then: isinstance(__return__, str)
        """
        return "%s(%s, %s)" % (self.__call, self.__args, self.__kwargs)

    def __call__(self):
        """
        ensure: __return__ is None
        """
        result = self.__call(*self.__args, **self.__kwargs)
        if result is not None:
            warnings.warn("discarded %s: %s" %
                    (pyc.fully_qualified_name(self.__call), result),
                    RuntimeWarning)


class future(object):
    """Todo.
    """

    __metaclass__ = dbc.dbc_class

    def __init__(self, call, *args, **kwargs):
        """
        require: isinstance(call, collections.Callable)
        ensure: not self.is_called()
        """
        super(future, self).__init__()
        self.__call = call
        self.__args = args
        self.__kwargs = kwargs
        self.__result = None
        self.__called = False
        self.__sync = threading.Condition()

    def __str__(self):
        """
        ensure_then: isinstance(__return__, str)
        """
        with self.__sync:
            return "%s(%s, %s)%s" % (self.__call, self.__args, self.__kwargs,
                     ": %s" %(self.__result) if self.__called else "")

    def __call__(self):
        """
        require: not self.is_called()
        ensure: self.is_called()
        ensure: __return__ is None
        """
        self.__result = self.__call(*self.__args, **self.__kwargs)
        with self.__sync:
            # check pre-condition with race-condition
            assert not self.__called, "%s may only be called once" % self
            self.__called = True
            self.__sync.notifyAll()

    def is_called(self):
        """
        ensure: isinstance(__return__, bool)
        """
        with self.__sync:
            return self.__called

    def get_result(self):
        """
        ensure: self.is_called()
        """
        with self.__sync:
            while not self.__called:
                self.__sync.wait()
            return self.__result


class active_object(object):
    """Todo.
    """

    __metaclass__ = dbc.dbc_class

    def __init__(self, name):
        """
        require: isinstance(name, str)
        ensure: not self.is_stopped()
        """
        super(active_object, self).__init__()
        # initialise the logging facility
        self.__log = logging.getLogger(pyc.fully_qualified_name(type(self)))
        # use deque for better performance of FIFO actions
        self.__actions = collections.deque()
        # create and start the thread of this active object
        self.__stop = False
        self.__sync = threading.Condition()
        self.__thd = threading.Thread(
                name = name,
                target = err.unhandled_exception_handler.handle,
                args = [self.__run])
        self.__thd.start()

    def __repr__(self):
        return pyc.generic_repr(self)

    def __str__(self):
        return pyc.generic_str(self)

    def __run(self):
        with self.__sync:
            while not self.__stop or len(self.__actions) > 0:
                if len(self.__actions) == 0:
                    self.__sync.wait()
                else:
                    act = self.__actions.popleft()
                    self.__log.debug(str(act))
                    with unsync(self.__sync):
                        act()

    def is_stopped(self):
        """
        ensure: isinstance(__return__, bool)
        """
        with self.__sync:
            return self.__stop

    def stop(self, block = False):
        """
        require: isinstance(block, bool)
        ensure: self.is_stopped()
        """
        with self.__sync:
            self.__stop = True
            self.__sync.notify()
        if block:
            self.__thd.join()

    def schedule(self, act):
        """
        require: isinstance(act, collections.Callable)
        require: not self.is_stopped()
        ensure: __return__ is act
        """
        with self.__sync:
            # check pre-condition with race-condition
            assert not self.__stop, "%s may not be stopped" % self
            self.__actions.append(act)
            if len(self.__actions) == 1:
                self.__sync.notify()
        return act

