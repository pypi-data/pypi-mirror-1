"""Color output plugin for the nose testing framework.

Use ``nosetests --with-color`` (no "u"!) to turn it on.

http://en.wikipedia.org/wiki/Rudolph_the_Red-Nosed_Reindeer

"Rudolph the Red-Nosed Reindeer" is a popular Christmas story about Santa
Claus' ninth and lead reindeer who possesses an unusually red colored nose that
gives off its own light that is powerful enough to illuminate the team's path
through inclement weather.


Copyright 2007 John J. Lee <jjl@pobox.com>

This code is derived from zope.testing version 3.5.0, which carries the
following copyright and licensing notice:

##############################################################################
#
# Copyright (c) 2004-2006 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""

import doctest
import os
import re
import sys
import time
import traceback
import unittest

import nose.config
import nose.core
import nose.plugins
import nose.util

# TODO
# syntax-highlight traceback Python source lines


__version__ = "0.2a"
__revision__ = "$Id: rudolf.py 48756 2007-11-17 13:57:24Z jjlee $"


def normalize_path(pathname):
    if hasattr(os.path, "realpath"):
        pathname = os.path.realpath(pathname)
    return os.path.normcase(os.path.abspath(pathname))


def relative_location(basedir, target, posix_result=True):
    """
    >>> relative_location("/a/b/", "/a/b/c")
    'c'
    >>> relative_location("a/b", "a/b/c/d")
    'c/d'
    >>> relative_location("/z", "/a/b")
    '../a/b'

    >>> this_dir = os.path.dirname(normalize_path(__file__))
    >>> relative_location("/a/b/", "a/b/c") == "../.." + this_dir + "/a/b/c"
    True

    >>> nr_dirs_up_to_root = os.path.join(this_dir, "a", "b").count(os.sep)
    >>> expected = "/".join([".."] * nr_dirs_up_to_root) + "/a/b/c/d"
    >>> relative_location("a/b", "/a/b/c/d/") == expected
    True
    """
    # based on a function by Robin Becker
    import os.path, posixpath
    basedir = normalize_path(basedir)
    target = normalize_path(target)
    baseparts = basedir.split(os.sep)
    targetparts = target.split(os.sep)
    nr_base = len(baseparts)
    nr_target = len(targetparts)
    nr_common = min(nr_base, nr_target)
    ii = 0
    while ii < nr_common and baseparts[ii] == targetparts[ii]:
        ii += 1
    relative_parts = (nr_base-ii)*['..'] + targetparts[ii:]
    if posix_result:
        return posixpath.join(*relative_parts)
    else:
        return os.path.join(*relative_parts)


def elide_foreign_path_and_line_nr(base_dir, path, line_nr):
    relpath = relative_location(base_dir, path)
    if ".." in relpath:
        filename = os.path.basename(relpath)
        return os.path.join("...", filename), "..."
    else:
        return relpath, line_nr


class DocTestFailureException(AssertionError):
    """Custom exception for doctest unit test failures."""


# colour output code taken from zope.testing, and hacked

class ColorfulOutputFormatter(object):
    """Output formatter that uses ANSI color codes.

    Like syntax highlighting in your text editor, colorizing
    test failures helps the developer.
    """

    separator1 = "=" * 70
    separator2 = "-" * 70

    doctest_template = """
File "%s", line %s, in %s

%s
Want:
%s
Got:
%s
"""

    # These colors are carefully chosen to have enough contrast
    # on terminals with both black and white background.
    colorscheme = {"normal": "normal",
                   "pass": "green",
                   "failure": "magenta",
                   "error": "brightred",
                   "number": "green",
                   "ok-number": "green",
                   "error-number": "brightred",
                   "filename": "lightblue",
                   "lineno": "lightred",
                   "testname": "lightcyan",
                   "failed-example": "cyan",
                   "expected-output": "green",
                   "actual-output": "red",
                   "added": "green",
                   "removed": "red",
                   "character-diffs": "magenta",
                   "diff-chunk": "magenta",
                   "exception": "red"}

    # Map prefix character to color in diff output.  This handles ndiff and
    # udiff correctly, but not cdiff.
    diff_color = {"-": "removed",
                  "+": "added",
                  "?": "character-diffs",
                  "@": "diff-chunk",
                  "*": "diff-chunk",
                  "!": "actual-output",}

    prefixes = [("dark", "0;"),
                ("light", "1;"),
                ("bright", "1;"),
                ("bold", "1;"),]

    colorcodes = {"default": 0, "normal": 0,
                  "black": 30,
                  "red": 31,
                  "green": 32,
                  "brown": 33, "yellow": 33,
                  "blue": 34,
                  "magenta": 35,
                  "cyan": 36,
                  "grey": 37, "gray": 37, "white": 37}

    def __init__(self, verbosity, descriptions, stream=sys.stdout,
                 clean_tracebacks=False, base_dir=False):
        self._stream = stream
        self._verbose = bool(verbosity)
        self._show_all = verbosity > 1
        self._dots = verbosity == 1
        self._descriptions = descriptions
        self._clean_tracebacks = clean_tracebacks
        self._base_dir = base_dir

    def color_code(self, color):
        """Convert a color description (e.g. 'lightgray') to a terminal code.
        """
        prefix_code = ""
        for prefix, code in self.prefixes:
            if color.startswith(prefix):
                color = color[len(prefix):]
                prefix_code = code
                break
        color_code = self.colorcodes[color]
        return "\033[%s%sm" % (prefix_code, color_code)

    def color(self, what):
        """Pick a named color from the color scheme"""
        return self.color_code(self.colorscheme[what])

    def colorize(self, what, message, normal="normal"):
        """Wrap message in color."""
        return self.color(what) + message + self.color(normal)

    def set_output_stream(self, stream):
        self._stream = stream

    def get_description(self, test):
        if self._descriptions:
            return test.shortDescription() or str(test)
        else:
            return str(test)

    def start_test(self, test):
        if self._show_all:
            self._stream.write(self.colorize("normal",
                                             self.get_description(test)))
            self._stream.write(self.colorize("normal", " ... "))
        self._stream.flush()

    def test_success(self, test):
        if self._show_all:
            self._stream.writeln(self.colorize("pass", "ok"))
        elif self._dots:
            self._stream.write(self.colorize("pass", "."))

    def test_error(self, test, exc_info, label):
        if self._show_all:
            self._stream.writeln(self.colorize("error", label))
        elif self._dots:
            self._stream.write(self.colorize("error", label[:1]))

    def test_failure(self, test, exc_info):
        if self._show_all:
            self._stream.writeln(self.colorize("failure", "FAIL"))
        elif self._dots:
            self._stream.write(self.colorize("failure", "F"))

    def print_error_list(self, flavour, errors):
        problem_color = (flavour == "FAIL") and "failure" or "error"
        for test, err, err_type in errors:
            self._stream.writeln(self.separator1)
            self._stream.writeln("%s: %s" % (
                    self.colorize(problem_color, flavour),
                    self.get_description(test)))
            self._stream.writeln(self.separator2)
            self.print_traceback(err, err_type)

    def print_summary(self, success, summary, tests_run, start, stop):
        write = self._stream.write
        writeln = self._stream.writeln
        writelines = self._stream.writelines
        taken = float(stop - start)
        plural = tests_run != 1 and "s" or ""
        count_color = success and "ok-number" or "error-number"

        writeln(self.separator2)
        writelines([
                "Ran ",
                self.colorize(count_color, "%s " % tests_run),
                "test%s in " % plural,
                self._format_seconds(taken)])
        writeln()
        if not success:
            write(self.colorize("failure", "FAILED"))
            write(" (")
            any = False
            for label, count in summary.items():
                if not count:
                    continue
                if any:
                    write(", ")
                write("%s=" % label)
                problem_color = (label == "failures") and "failure" or "error"
                write(self.colorize(problem_color, str(count)))
                any = True
            writeln(")")
        else:
            writeln(self.colorize("pass", "OK"))

    def _format_seconds(self, n_seconds, normal="normal"):
        """Format a time in seconds."""
        if n_seconds >= 60:
            n_minutes, n_seconds = divmod(n_seconds, 60)
            return "%s minutes %s seconds" % (
                        self.colorize("number", "%d" % n_minutes, normal),
                        self.colorize("number", "%.3f" % n_seconds, normal))
        else:
            return "%s seconds" % (
                        self.colorize("number", "%.3f" % n_seconds, normal))

    def format_traceback(self, exc_info):
        """Format the traceback."""
        v = exc_info[1]
        if isinstance(v, DocTestFailureException):
            tb = v.args[0]
        if isinstance(v, doctest.DocTestFailure):
            # XXX
#             if self._clean_tracebacks:
#                 filename, lineno = elide_foreign_path_and_line_nr(
#                     self._base_dir,
#                     v.test.filename,
#                     (v.test.lineno + v.example.lineno + 1))
            tb = self.doctest_template % (
                v.test.filename,
                v.test.lineno + v.example.lineno + 1,
                v.test.name,
                v.example.source,
                v.example.want,
                v.got,
                )
        else:
            tb = "".join(traceback.format_exception(*exc_info))
        return tb

    def print_traceback(self, formatted_traceback, err_type):
        """Report an error with a traceback."""
        if issubclass(err_type, DocTestFailureException):
            self.print_doctest_failure(formatted_traceback)
        else:
            self.print_colorized_traceback(formatted_traceback)

    def print_doctest_failure(self, formatted_failure):
        """Report a doctest failure.

        ``formatted_failure`` is a string -- that's what
        DocTestSuite/DocFileSuite gives us.
        """
        color_of_indented_text = 'normal'
        colorize_diff = False
        lines = formatted_failure.splitlines()

        # this first traceback in a doctest failure report is rarely
        # interesting, but it looks funny non-colourized so let's colourize it
        # anyway
        exc_lines = []
        while True:
            line = lines.pop(0)
            if line == self.separator2:
                break
            exc_lines.append(line)
        self.print_colorized_traceback("\n".join(exc_lines))
        print >>self._stream, self.separator2

        for line in lines:
            if line.startswith('File '):
                m = re.match(r'File "(.*)", line (\d*), in (.*)$', line)
                if m:
                    filename, lineno, test = m.groups()
                    if self._clean_tracebacks:
                        filename, lineno = elide_foreign_path_and_line_nr(
                            self._base_dir, filename, lineno)
                    self._stream.writelines([
                        self.color('normal'), 'File "',
                        self.color('filename'), filename,
                        self.color('normal'), '", line ',
                        self.color('lineno'), lineno,
                        self.color('normal'), ', in ',
                        self.color('testname'), test,
                        self.color('normal'), '\n'])
                else:
                    print >>self._stream, line
            elif line.startswith('    '):
                if colorize_diff and len(line) > 4:
                    color = self.diff_color.get(line[4],
                                                color_of_indented_text)
                    print >>self._stream, self.colorize(color, line)
                else:
                    print >>self._stream, self.colorize(color_of_indented_text,
                                                        line)
            else:
                colorize_diff = False
                if line.startswith('Failed example'):
                    color_of_indented_text = 'failed-example'
                elif line.startswith('Expected:'):
                    color_of_indented_text = 'expected-output'
                elif line.startswith('Got:'):
                    color_of_indented_text = 'actual-output'
                elif line.startswith('Exception raised:'):
                    color_of_indented_text = 'exception'
                elif line.startswith('Differences '):
                    color_of_indented_text = 'normal'
                    colorize_diff = True
                else:
                    color_of_indented_text = 'normal'
                print >>self._stream, line
        print >>self._stream

    def print_colorized_traceback(self, formatted_traceback):
        """Report a test failure.

        ``formatted_traceback`` is a string.
        """
        for line in formatted_traceback.splitlines():
            if line.startswith("  File"):
                m = re.match(r'  File "(.*)", line (\d*)(?:, in (.*))?$', line)
                if m:
                    filename, lineno, test = m.groups()
                    if self._clean_tracebacks:
                        filename, lineno = elide_foreign_path_and_line_nr(
                            self._base_dir, filename, lineno)
                    tb_lines = [
                        self.color("normal"), '  File "',
                        self.color("filename"), filename,
                        self.color("normal"), '", line ',
                        self.color("lineno"), lineno,
                        ]
                    if test:
                        # this is missing for the first traceback in doctest
                        # failure report
                        tb_lines.extend([
                                self.color("normal"), ", in ",
                                self.color("testname"), test,
                                ])
                    tb_lines.extend([
                            self.color("normal"), "\n",
                                    ])
                    self._stream.writelines(tb_lines)
                else:
                    print >>self._stream, line
            elif line.startswith("    "):
                print >>self._stream, self.colorize("failed-example", line)
            elif line.startswith("Traceback (most recent call last)"):
                print >>self._stream, line
            else:
                print >>self._stream, self.colorize("exception", line)
        print >>self._stream

    def stop_test(self, test):
        if self._verbose > 1:
            print >>self._stream
        self._stream.flush()

    def stop_tests(self):
        if self._verbose == 1:
            self._stream.write("\n")
        self._stream.flush()


class ColorOutputPlugin(nose.plugins.Plugin):

    name = "color"

    formatter_class = ColorfulOutputFormatter
    clean_tracebacks = False
    base_dir = None

    def __init__(self):
        nose.plugins.Plugin.__init__(self)
        self._result = None
        # for debugging
#         self.base_dir = os.path.dirname(__file__)
#     clean_tracebacks = True

    def options(self, parser, env=os.environ):
        nose.plugins.Plugin.options(self, parser, env)
        parser.add_option("--no-color", action="store_false",
                          dest="enable_plugin_color",
                          help="Don't output in color")
        # XXX This might be wrong when running tests in a subprocess (since I
        # guess sys.stdout will be a pipe, but colour output should be turned
        # on).  Depends on how the running-in-a-subprocess is done (it's not a
        # core nose feature as of version 0.10.0).
        action = sys.stdout.isatty() and "store_true" or "store_false"
        parser.add_option("--auto-color", action=action,
                          dest="enable_plugin_color",
                          help="Output in color only if stdout is a terminal.")

    def configure(self, options, conf):
        nose.plugins.Plugin.configure(self, options, conf)
        self._verbosity = conf.verbosity
        self._show_all = self._verbosity > 1
        self._dots = self._verbosity == 1

    def begin(self):
        self._old_failure_exception = doctest.DocTestCase.failureException
        # monkeypatch!
        doctest.DocTestCase.failureException = DocTestFailureException

    def setOutputStream(self, stream):
        self._stream = stream
        self._formatter = self.formatter_class(
            self._verbosity,
            True,
            self._stream,
            clean_tracebacks=self.clean_tracebacks,
            base_dir=self.base_dir)
        return unittest._WritelnDecorator(open(os.devnull, 'w'))

    def prepareTestResult(self, result):
        result.__failures = []
        result.__errors = []
        result.__tests_run = 0
        result.__start_time = 0
        result.__stop_time = 0
        self._result = result

    def startTest(self, test):
        self._result.__tests_run = self._result.__tests_run + 1
        self._formatter.start_test(test)
        self._result.__start_time = time.time()

    def addSuccess(self, test):
        self._result.__stop_time = time.time()
        self._formatter.test_success(test)

    def addFailure(self, test, err):
        self._result.__stop_time = time.time()
        formatted_failure = self._exc_info_to_string(err, test)
        self._result.__failures.append((test, formatted_failure, err[0]))
        self._formatter.test_failure(test, err)

    def addError(self, test, err):
        self._result.__stop_time = time.time()
        # If the exception is a registered class, the error will be added to
        # the list for that class, not errors.
        formatted_err = self._formatter.format_traceback(err)
        for cls, (storage, label, isfail) in self._result.errorClasses.items():
            if issubclass(err[0], cls):
                storage.append((test, formatted_err, err[0]))
                self._formatter.test_error(test, err, label)
                return
        self._result.__errors.append((test, formatted_err, err[0]))
        self._formatter.test_error(test, err, "ERROR")

    def stopTest(self, test):
        self._formatter.stop_test(test)

    def report(self, stream):
        self._print_errors()
        self._print_summary(self._result.__start_time,
                            self._result.__stop_time)
        self._result = None

    def finalize(self, result):
        self._formatter.stop_tests()
        # remove monkeypatch
        doctest.DocTestCase.failureException = self._old_failure_exception

    def _print_errors(self):
        if self._dots or self._show_all:
            self._stream.writeln()
        self._formatter.print_error_list("ERROR", self._result.__errors)
        self._formatter.print_error_list("FAIL", self._result.__failures)
        for cls in self._result.errorClasses.keys():
            storage, label, isfail = self._result.errorClasses[cls]
            self._formatter.print_error_list(label, storage)

    def _print_summary(self, start, stop):
        success = self._result.wasSuccessful()
        summary = nose.util.odict()
        if not success:
            summary["failures"], summary["errors"] = \
                map(len, [self._result.__failures, self._result.__errors])
            for cls in self._result.errorClasses.keys():
                storage, label, isfail = self._result.errorClasses[cls]
                if not isfail:
                    continue
                summary[label] = len(storage)
        self._formatter.print_summary(success, summary,
                                      self._result.__tests_run, start, stop)

    def _exc_info_to_string(self, err, test):
        exctype, value, tb = err
        # Skip test runner traceback levels
        while tb and self._is_relevant_tb_level(tb):
            tb = tb.tb_next
        if exctype is test.failureException:
            # Skip assert*() traceback levels
            length = self._count_relevant_tb_levels(tb)
            return ''.join(traceback.format_exception(exctype, value, tb,
                                                      length))
        return ''.join(traceback.format_exception(exctype, value, tb))

    def _is_relevant_tb_level(self, tb):
        return tb.tb_frame.f_globals.has_key('__unittest')

    def _count_relevant_tb_levels(self, tb):
        length = 0
        while tb and not self._is_relevant_tb_level(tb):
            length += 1
            tb = tb.tb_next
        return length


# classes for use in rudolf's own tests


class TestColorfulOutputFormatter(ColorfulOutputFormatter):

    __test__ = False

    def _format_seconds(self, n_seconds, normal="normal"):
        return "%s seconds" % (self.colorize("number", "...", normal))


class TestColorOutputPlugin(ColorOutputPlugin):

    __test__ = False

    formatter_class = TestColorfulOutputFormatter
    clean_tracebacks = True

    def __init__(self):
        ColorOutputPlugin.__init__(self)
        self.base_dir = os.path.dirname(__file__)
