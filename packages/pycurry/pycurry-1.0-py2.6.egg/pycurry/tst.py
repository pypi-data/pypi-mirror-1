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

from __future__ import print_function

import os
import sys
import inspect
import threading
import cProfile
import pstats
import logging
import logging.config
import unittest
import collections # pylint: disable-msg=W0611
import optparse

import pycurry as pyc
import pycurry.dbc as dbc
import pycurry.err as err


class pylint(object):
    """Performs static analysis on the specified data using the specified
    configuration.
    """

    __metaclass__ = dbc.dbc_class

    url = "http://www.logilab.org/project/pylint"
    cfg = "pycurry/pylint.ini"

    def __init__(self, data, config = cfg):
        """
        The specified data must denote a package or a module.

        require: inspect.ismodule(data) or isinstance(data, str)
        require: isinstance(config, str)
        """
        super(pylint, self).__init__()
        try:
            from pylint import lint
            lint.Run([
                "--rcfile=%s" % pyc.resolve_filename(config),
                data.__name__ if inspect.ismodule(data) else data
            ])
        except ImportError:
            print("install pylint from '%s'" % self.url,
                  file = sys.stderr)
            raise
        except SystemExit:
            pass # do not exit, but allow dynamic testing


class text_test_runner(unittest.TextTestRunner):
    """Runner that also collects unhandled exceptions of other threads. The 
    unittest.TextTestRunner does not collect statistics from other threads
    then the thread that calls its run method. This specialized class allows,
    in combination with the unittest_exception_handler, you to collect all
    errors from all threads. It can be used as follows:

        runner = pycurry.tst.text_test_runner()
        pycurry.err.unhandled_exception_handler.prepend_handler(
            pycurry.err.unittest_exception_handler(runner.result))
        runner.run(suite())

    Where suite() is a function that returns a test-suite with test-cases.
    Note that the other threads of the program must be handled by the
    pycurry.err.unhandled_exception_handler.handle() function otherwise the
    unhandled exceptions will not be collected.
    """

    def __init__(self, stream = sys.stderr, descriptions = 1, verbosity = 1):
        """Initialise a text_test_runner object. The parameters are passed 1:1 
        to the unittest.TextTestRunner class.
        """
        super(text_test_runner, self).__init__(stream, descriptions, verbosity)
        self.__result = super(text_test_runner, self)._makeResult()

    @property
    def result(self):
        """The test result of this runner in which the unhandled exceptions can
        be stored.
        """
        return self.__result

    def _makeResult(self):
        """Overriden to use the same test result object between the unittest
        module and the pycurry.err module.
        """
        return self.result


class coverage(object):
    """Context manager to measure coverage on the specified modules.
    """

    __metaclass__ = dbc.dbc_class

    url = "http://nedbatchelder.com/code/modules/coverage.html"

    def __init__(self, modules, stream = sys.stdout):
        """
        require: isinstance(modules, collections.Iterable)
        require: not [mod for mod in modules if not inspect.ismodule(mod)]
        require: hasattr(stream, "write")
        """
        super(coverage, self).__init__()
        self.__mods = modules
        self.__strm = stream
        try:
            import coverage as cov
        except ImportError:
            print("install coverage from '%s'" % self.url,
                  file = sys.stderr)
            raise
        self.__impl = cov
        self.__impl.exclude("if True:")
        self.__impl.exclude("assert None")
        self.__impl.exclude("except ImportError")
        self.__impl.exclude("raise NotImplementedError")

    def __enter__(self):
        if True: # to exclude from coverage
            self.__impl.erase()
            self.__impl.start()
            for mod in self.__mods:
                try:
                    reload(mod)
                except ImportError:
                    pass

    def __exit__(self, _1, _2, _3):
        if True: # to exclude from coverage
            self.__impl.stop()
            self.__impl.report(self.__mods, file = self.__strm)


class profiler(object):
    """Todo.
    """

    __metaclass__ = dbc.dbc_class

    def __init__(self):
        """
        require: False
        """
        assert None, "object creation not allowed"

    calls = "calls"
    callers = "callers"
    callees = "callees"
    time = "cumulative"

    __mods = ""
    __info = [calls]
    __sort = calls
    __strm = sys.stdout
    __stat = None
    __data = set()
    __sync = threading.Condition()

    @classmethod
    @dbc.dbc_function
    def __filename(cls):
        """
        ensure: isinstance(__return__, str)
        """
        thd = threading.current_thread()
        if thd.ident is None:
            thd = "" # the 'main' thread
        else:
            thd = "_t@%04x" % thd.ident
        return ".profile_p@%04x%s" % (os.getpid(), thd)

    @classmethod
    @dbc.dbc_function
    def init(cls, modules, info, sort, stream = sys.stdout):
        """
        require: isinstance(modules, collections.Iterable)
        require: not [mod for mod in modules if not inspect.ismodule(mod)]
        require: isinstance(info, collections.Iterable)
        require: not [inf for inf in info \
                if not inf in (cls.calls, cls.callers, cls.callees)]
        require: sort in (cls.calls, cls.time)
        require: hasattr(stream, "write")
        """
        with cls.__sync:
            for mod in modules:
                if hasattr(mod, "__file__"):
                    if len(cls.__mods) != 0:
                        cls.__mods += "|"
                    cls.__mods += os.path.splitext(mod.__file__.replace(
                        "\\", "\\\\").replace(".", "\\."))[0]
            cls.__info = info
            cls.__sort = sort
            cls.__strm = stream
            err.unhandled_exception_handler.set_proxy(cls.profile)

    @classmethod
    @dbc.dbc_function
    def profile(cls, call, *args, **kwargs):
        """
        require: isinstance(call, collections.Callable)
        """
        # get the file for this thread
        with cls.__sync:
            data = cls.__filename()
            cls.__data.add(data)
        # run the (undocumented) profiler on the specified function
        impl = cProfile.Profile()
        result = impl.runcall(call, *args, **kwargs)
        impl.dump_stats(data)
        # use the profiled data
        with cls.__sync:
            if cls.__stat is None:
                cls.__stat = pstats.Stats(data, stream = cls.__strm)
            else:
                cls.__stat.add(data)
            cls.__data.remove(data)
            if len(cls.__data) == 0:
                cls.__stat.sort_stats("module", cls.__sort, "line")
                for info in cls.__info:
                    if info == cls.calls:
                        cls.__stat.print_stats(cls.__mods)
                    elif info == cls.callers:
                        cls.__stat.print_callers(cls.__mods)
                    elif info == cls.callees:
                        cls.__stat.print_callees(cls.__mods)
                    else:
                        assert None, "unknown info '%s'" % info
        return result


def main(suite, modules, package = None):
    """
    require: isinstance(suite, unittest.TestSuite)
    require: isinstance(modules, collections.Iterable)
    require: not [mod for mod in modules if not inspect.ismodule(mod)]
    require: inspect.ismodule(package)
    """
    # scan the command line
    parser = optparse.OptionParser(description =
            "Run your tests with optional static and dynamic analysis.")
    parser.add_option("-v", "--verbose", action = "store_true",
            help = "name the tests executing")
    parser.add_option("-d", "--debug", action = "store_true",
            help = "run the test in debug mode")
    parser.add_option("-l", "--logging",
            help = "the logging configuration file to use")
    parser.add_option("--lint", action = "store_true",
            help = "perform static analysis on the code to test")
    parser.add_option("--lintrc",
            help = "the lint configuration file to use")
    parser.add_option("-c", "--coverage", action = "store_true",
            help = "measure code coverage on the code to test")
    parser.add_option("-p", "--profiling", action = "store_true",
            help = "measure performance profiling on the code to test")
    parser.add_option("--statistics", action = "append",
            choices = (profiler.calls, profiler.callers, profiler.callees),
            help = "which profiling statistics to analyse")
    parser.add_option("--sort",
            choices = (profiler.calls, profiler.time),
            help = "sort on number of calls or on cumulative time")
    parser.set_defaults(
            verbose = False,
            debug = False,
            logging = "pycurry/log.ini",
            lint = False,
            lintrc = pylint.cfg,
            coverage = False,
            profiling = False,
            statistics = [profiler.calls],
            sort = profiler.calls)
    options, args = parser.parse_args()
    # check the command line
    if len(args) > 0:
        parser.error("no arguments defined: %s" % args)
    if options.debug and options.coverage:
        parser.error("options 'debug' and 'coverage' are mutual exclusive")
    if options.debug and options.profiling:
        parser.error("options 'debug' and 'profiling' are mutual exclusive")
    if options.coverage and options.profiling:
        parser.error("options 'coverage' and 'profiling' are mutual exclusive")
    loggingrc = pyc.resolve_filename(options.logging)
    if loggingrc is None:
        parser.error("cannot find logging configuration file: '%s'" 
                % options.logging)
    lintrc = pyc.resolve_filename(options.lintrc)
    if lintrc is None:
        parser.error("cannot find lint configuration file: '%s'" 
                % options.lintrc)
    # parse the command line
    #   first set the test configuration
    logging.config.fileConfig(loggingrc)
    err.unhandled_exception_handler.append_handler(
            err.print_exception_handler())
    if options.debug:
        err.unhandled_exception_handler.append_handler(
                err.pdb_exception_handler())
    else:
        err.unhandled_exception_handler.append_handler(
                err.log_exception_handler())
    #   optionally perform static analysis
    if options.lint:
        if package is not None:
            pylint(package, lintrc)
        else:
            for module in modules:
                pylint(module, lintrc)
    #   then perform dynamic analysis
    if options.debug:
        suite.debug()
    else:
        runner = text_test_runner(verbosity = (2 if options.verbose else 1))
        err.unhandled_exception_handler.prepend_handler(
                err.unittest_exception_handler(runner.result))
        if options.coverage:
            with coverage(modules):
                runner.run(suite)
        elif options.profiling:
            profiler.init(modules, options.statistics, options.sort)
            profiler.profile(runner.run, suite)
        else:
            runner.run(suite)

