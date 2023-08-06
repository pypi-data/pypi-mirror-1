"""Module for handling unhandled exceptions from multiple threads.

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

from __future__ import print_function

import os
import sys
import logging
import warnings
import unittest
import traceback
import threading
import contextlib
import collections # pylint: disable-msg=W0611

import pycurry as pyc
import pycurry.dbc as dbc


class exception_handler(object):
    """Base class for exception handling strategies.
    """

    __metaclass__ = dbc.dbc_class

    @classmethod
    @dbc.dbc_function
    def format_thd(cls, exc_thd):
        """Formats the thread information as a string.

        require: isinstance(exc_thd, threading.Thread)
        ensure: isinstance(__return__, str)
        """
        return "Unhandled exception in thread %s(%s):\n" % (
                exc_thd.name, exc_thd.ident)

    @classmethod
    @dbc.dbc_function
    def format_exc(cls, exc_type, exc_value, exc_traceback):
        """Formats the exception information as a string.

        ensure: isinstance(__return__, str)
        """
        result = ""
        for res in traceback.format_exception(
                exc_type, exc_value, exc_traceback):
            result += res
        return result

    @classmethod
    @dbc.dbc_function
    def format(cls, exc_thd, exc_type, exc_value, exc_traceback):
        """Formats both the thread and exception information as a string.

        ensure: isinstance(__return__, str)
        """
        return cls.format_thd(exc_thd) + cls.format_exc(
                exc_type, exc_value, exc_traceback)

    def __init__(self):
        """Initialise an exception_handler object.
        """
        super(exception_handler, self).__init__()

    def handle(self, exc_thd, exc_type, exc_value, exc_traceback):
        """Does nothing by default. It has been chosen to provide the handle 
        methods of the different exception strategies all exception 
        information allowing any implementation possible.
        """
        raise NotImplementedError


class print_exception_handler(exception_handler):
    """Prints to the console.
    """

    def __init__(self, strm = sys.stderr):
        """Initialise a print_exception_handler object. By default, this 
        handler will print to stderr file of the console.

        require: hasattr(strm, "write")
        """
        super(print_exception_handler, self).__init__()
        self.__strm = strm

    def handle(self, exc_thd, exc_type, exc_value, exc_traceback):
        """Prints the unhandled exception information to the file.
        """
        print(self.format(exc_thd, exc_type, exc_value, exc_traceback),
                file = self.__strm)


class log_exception_handler(exception_handler):
    """Logs to the logging module. Uses the default installed 'logging' module.
    """

    def __init__(self):
        """Initialise a log_exception_handler object.
        """
        super(log_exception_handler, self).__init__()

    def handle(self, exc_thd, exc_type, exc_value, exc_traceback):
        """Logs a critical message in the logger for this class.
        """
        logging.getLogger(pyc.fully_qualified_name(type(self))).exception(
                self.format_thd(exc_thd))


class gmail_exception_handler(exception_handler):
    """Mails the exception information. The free GMail SMTP server is used.
    """

    def __init__(self, user, password, addrs):
        """Initialise a gmail_exception_handler object. The user/password must 
        denote a valid gmail account.

        require: isinstance(user, str)
        require: isinstance(password, str)
        require: isinstance(addrs, str) or \
                (isinstance(addrs, collections.Iterable) and \
                 not [addr for addr in addrs if not isinstance(addr, str)])
        """
        super(gmail_exception_handler, self).__init__()
        self.__host = "smtp.gmail.com"
        self.__user = user
        self.__pass = password
        self.__toes = addrs
        self.__mail = None
        # test the connection
        with self.__connect():
            pass

    @contextlib.contextmanager
    def __connect(self):
        import smtplib
        # enter
        self.__mail = smtplib.SMTP(self.__host)
        self.__mail.set_debuglevel(0)
        self.__mail.ehlo()
        self.__mail.starttls()
        self.__mail.ehlo()
        self.__mail.login(self.__user, self.__pass)
        # block
        try:
            yield 
        finally:
            # exit
            self.__mail.quit()

    def handle(self, exc_thd, exc_type, exc_value, exc_traceback):
        """Sends an e-mail with the exception information to the specified
        addresses.
        """
        with self.__connect():
            import socket
            import email.message
            msg = email.message.Message()
            msg["From"] = self.__user
            msg["Subject"] = \
                    "Unhandled exception on [%s]" % socket.gethostname()
            msg.set_payload(
                    self.format(exc_thd, exc_type, exc_value, exc_traceback))
            self.__mail.sendmail(self.__user, self.__toes, msg.as_string())


class pdb_exception_handler(exception_handler):
    """Starts the Python debugger. Uses is the default installed 'pdb' module
    """

    def __init__(self):
        """Initialise a pdb_exception_handler object.
        """
        super(pdb_exception_handler, self).__init__()

    def handle(self, exc_thd, exc_type, exc_value, exc_traceback):
        """Enter post-mortem debugging of the specified exception.
        """
        if True: # to exclude this block from coverage
            import pdb
            pdb.post_mortem(exc_traceback)


class winpdb_exception_handler(exception_handler):
    """Starts the winpdb debugger. You need to install the rpdb2 module from 
    http://winpdb.org in order to use this exception handler.
    """

    def __init__(self):
        """Initialise a winpdb_exception_handler object.
        """
        super(winpdb_exception_handler, self).__init__()
        # test the installation
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            try:
                import rpdb2 # pylint: disable-msg=W0612
            except ImportError:
                print("install winpdb from http://winpdb.org",
                        file = sys.stderr)
                raise
        # get the path to the debugger script
        if os.name == "nt":
            self.__path = os.path.join(sys.prefix, "Scripts", "winpdb_.pyw")
        else:
            assert None, "unknown platform [%s]" % os.name
        assert os.path.isfile(self.__path), "not a file [%s]" % self.__path

    def handle(self, exc_thd, exc_type, exc_value, exc_traceback):
        """Attaches the winpdb debugger to this script execution.
        """
        if True: # to exclude this block from coverage
            # first start the client debugger
            import subprocess
            subprocess.Popen((sys.executable,
                "-W ignore::DeprecationWarning::", self.__path))
            # then start the server debuggee
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", DeprecationWarning)
                import rpdb2
                rpdb2.start_embedded_debugger_interactive_password()


class unittest_exception_handler(exception_handler):
    """Adds exception to a unittest test result.
    """

    def __init__(self, test_result):
        """Initialise an unittest_exception_handler object.

        require: isinstance(test_result, unittest.TestResult)
        """
        super(unittest_exception_handler, self).__init__()
        self.__result = test_result
        self.__test = unittest.TestCase(methodName = "fail")

    def handle(self, exc_thd, exc_type, exc_value, exc_traceback):
        """Adds the exception as an error to the test result.
        """
        self.__test._testMethodDoc = self.format_thd(exc_thd)
        self.__result.addError(
                self.__test, (exc_type, exc_value, exc_traceback))


class exit_exception_handler(exception_handler):
    """Exits the interpreter.
    """

    def __init__(self):
        """Initialise a exit_exception_handler object.
        """
        super(exit_exception_handler, self).__init__()

    def handle(self, exc_thd, exc_type, exc_value, exc_traceback):
        """All threads will be terminated, daemon or not.
        """
        logging.shutdown()
        sys.exit()


class unhandled_exception_handler(object):
    """Aggregation of exception handlers for handling unhandled exceptions. As
    there can only exist one unhandled exception handler within the program,
    this class contains only static methods. Initially there are no exception
    handlers set.
    """

    __metaclass__ = dbc.dbc_class

    def __init__(self):
        """
        require: False
        """
        assert None, "object creation not allowed" 

    __proxy = None
    __handlers = []
    __sync = threading.Condition()

    @classmethod
    @dbc.dbc_function
    def set_proxy(cls, proxy):
        """Set a proxy to call the actual callable.

        require: proxy is None or isinstance(proxy, collections.Callable)
        """
        with cls.__sync:
            cls.__proxy = proxy

    @classmethod
    @dbc.dbc_function
    def has_handler(cls, handler):
        """Is the specified handler installed as an unhandled exception
        handler.

        require: isinstance(handler, exception_handler)
        ensure: isinstance(__return__, bool)
        """
        with cls.__sync:
            return handler in cls.__handlers

    @classmethod
    @dbc.dbc_function
    def prepend_handler(cls, handler):
        """Adds the handler as the first unhandled exception handler.

        require: isinstance(handler, exception_handler)
        require: not cls.has_handler(handler)
        ensure: cls.has_handler(handler)
        """
        with cls.__sync:
            cls.__handlers.insert(0, handler)

    @classmethod
    @dbc.dbc_function
    def append_handler(cls, handler):
        """Adds the handler as the last unhandled exception handler.

        require: isinstance(handler, exception_handler)
        require: not cls.has_handler(handler)
        ensure: cls.has_handler(handler)
        """
        with cls.__sync:
            cls.__handlers.append(handler)

    @classmethod
    @dbc.dbc_function
    def remove_handler(cls, handler):
        """Removes the handler.

        require: isinstance(handler, exception_handler)
        require: cls.has_handler(handler)
        ensure: not cls.has_handler(handler)
        """
        with cls.__sync:
            cls.__handlers.remove(handler)

    @classmethod
    @dbc.dbc_function
    def clear_handlers(cls):
        """Removes all exception handlers.
        """
        with cls.__sync:
            del cls.__handlers[:]

    @classmethod
    @dbc.dbc_function
    def handle(cls, call, *args, **kwargs):
        """Calls the specified callable. Any exceptions that are not handled 
        by the callable itself are handled here by forwarding them to the 
        added exception handlers from first to last. It has been chosen to 
        retrieve the exception information here only once to avoid problems 
        with possible nested exceptions when handling this exception.

        require: isinstance(call, collections.Callable)
        """ 
        # pylint: disable-msg=W0702
        try:
            if cls.__proxy is None:
                call(*args, **kwargs)
            else:
                cls.__proxy(call, *args, **kwargs)
        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            handle(exc_type, exc_value, exc_traceback)


@dbc.dbc_function
def handle(exc_type, exc_value, exc_traceback):
    """Todo.
    """
    # pylint: disable-msg=E1101,W0212
    # make a copy of the handlers to work with
    with unhandled_exception_handler._unhandled_exception_handler__sync:
        handlers = unhandled_exception_handler. \
                _unhandled_exception_handler__handlers[:]
    # handle the exception un-synchronized
    if len(handlers) > 0:
        exc_thd = threading.currentThread()
        for handler in handlers:
            handler.handle(exc_thd, exc_type, exc_value, exc_traceback)
    else:
        # call the handler installed at program startup
        sys.__excepthook__(exc_type, exc_value, exc_traceback)


# install the unhandled exception handler for the main thread
sys.excepthook = handle

