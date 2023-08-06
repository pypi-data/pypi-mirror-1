"""Logging utilities extending the standard logging module.

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
import logging.handlers
import collections

import pycurry as pyc
import pycurry.dbc as dbc


class rotating_memory_handler(logging.Handler, object):
    """In-memory logging facility that only logs in case of a certain level.
    """

    __metaclass__ = dbc.dbc_class

    def __init__(self, capacity = 1000, level = logging.WARNING,
            target = logging.handlers.RotatingFileHandler, *args, **kwargs):
        """Initialises a rotating_memory_handler object.
        The capacity specifies the maximum number of log records this handler 
        can hold. The level specifies upon which level a record must have to 
        be logged. The target specifies the class to instantiate, passing it 
        any provided arguments, for obtaining the handler to actually log to.

        require: isinstance(capacity, int)
        require: capacity > 0
        require: level in (logging.NOTSET, logging.DEBUG, logging.INFO, \
                logging.WARNING, logging.ERROR, logging.CRITICAL)
        require: hasattr(target, "setFormatter")
        require: hasattr(target, "emit")
        require: hasattr(target, "flush")
        """
        logging.Handler.__init__(self)
        self.__buf = collections.deque(maxlen = capacity)
        self.__lvl = level
        self.__trg = target(*args, **kwargs)
        self.__new = getattr(self.__trg, "doRollover", pyc.pass_)

    def __repr__(self):
        return pyc.generic_repr(self)

    def __str__(self):
        return pyc.generic_str(self)

    def setFormatter(self, form):
        """Forwards the formatter to the target handler.
        """
        logging.Handler.setFormatter(self, form)
        self.__trg.setFormatter(form)

    def emit(self, record):
        """Stores the record in this handler's buffer. In case the record's
        level matches the minimum logging level specified for this handler the
        buffer is emitted to the target handler.
        """
        self.__buf.append(record)
        if record.levelno >= self.__lvl:
            for rec in self.__buf:
                self.__trg.emit(rec)
            self.flush()
            self.__new()

    def flush(self):
        """Silently removes all logging from this handler's buffer.
        """
        self.__buf.clear()
        self.__trg.flush()

