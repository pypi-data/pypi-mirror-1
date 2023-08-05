Colorful output
===============

If you're on a Unix-like system, you can ask for colorized output.  The test
runner emits terminal control sequences to highlight important pieces of
information (such as the names of failing tests) in different colors.

    >>> import os.path, sys

    >>> import rudolf

    >>> directory_with_tests = os.path.join(os.path.dirname(__file__),
    ...                                     "test-support")

Since it wouldn't be a good idea to have terminal control characters in a
test file, let's wrap sys.stdout in a simple terminal interpreter

    >>> import re
    >>> class Terminal(object):
    ...     _color_regexp = re.compile('\033[[]([0-9;]*)m')
    ...     _colors = {'0': 'normal', '1': 'bold', '30': 'black', '31': 'red',
    ...                '32': 'green', '33': 'yellow', '34': 'blue',
    ...                '35': 'magenta', '36': 'cyan', '37': 'grey'}
    ...     def __init__(self, stream):
    ...         self._stream = stream
    ...     def __getattr__(self, attr):
    ...         return getattr(self._stream, attr)
    ...     def write(self, text):
    ...         if '\033[' in text:
    ...             text = self._color_regexp.sub(self._color, text)
    ...         self._stream.write(text)
    ...     def writelines(self, lines):
    ...         for line in lines:
    ...             self.write(line)
    ...     def _color(self, match):
    ...         colorstring = '{'
    ...         for number in match.group(1).split(';'):
    ...             colorstring += self._colors.get(number, '?')
    ...         return colorstring + '}'

    >>> real_stdout = sys.stdout
    >>> sys.stdout = Terminal(sys.stdout)

We don't want to remove tracebacks from the output like or remove the
test timing like nose.plugins.plugintest.run(), so we use a modified
version.

    >>> def run(*arg, **kw):
    ...     from cStringIO import StringIO
    ...     from nose import run
    ...     from nose.config import Config
    ...     from nose.plugins.manager import PluginManager
    ...
    ...     buffer = StringIO()
    ...     if 'config' not in kw:
    ...         plugins = kw.pop('plugins', None)
    ...         env = kw.pop('env', {})
    ...         manager = PluginManager(plugins=plugins)
    ...         kw['config'] = Config(env=env, plugins=manager)
    ...     if 'argv' not in kw:
    ...         kw['argv'] = ['nosetests', '-v']
    ...     kw['config'].stream = buffer
    ...     run(*arg, **kw)
    ...     out = buffer.getvalue()
    ...     print out.strip()

--no-color

--auto-color

A successful test run.  The "ok"s and numbers come out in green.

    >>> from nose.plugins.doctests import Doctest

    >>> plugins = [rudolf.TestColorOutputPlugin(), Doctest()]

    >>> run(argv=["nosetests", "-v", "--with-color",
    ...           "--with-doctest", "--doctest-extension", ".rst",
    ...           os.path.join(directory_with_tests, "passing")],
    ...     plugins=plugins)
    ...     # doctest: +REPORT_NDIFF
    {normal}Doctest: passing_doctest.rst{normal}{normal} ... {normal}{green}ok{normal}
    {normal}passing_tests.passing_test_1{normal}{normal} ... {normal}{green}ok{normal}
    {normal}passing_tests.passing_test_2{normal}{normal} ... {normal}{green}ok{normal}
    <BLANKLINE>
    ----------------------------------------------------------------------
    Ran {green}3 {normal}tests in {green}...{normal} seconds
    {green}OK{normal}


Without the '-v' for "verbose", the dots are green:

    >>> run(argv=["nosetests", "--with-color",
    ...           "--with-doctest", "--doctest-extension", ".rst",
    ...           os.path.join(directory_with_tests, "passing")],
    ...     plugins=plugins)
    ...     # doctest: +REPORT_NDIFF
    {green}.{normal}{green}.{normal}{green}.{normal}
    ----------------------------------------------------------------------
    Ran {green}3 {normal}tests in {green}...{normal} seconds
    {green}OK{normal}


A failed test highlights the errors and failures in magenta:

    >>> py = os.path.join(directory_with_tests, "failing", "failing_tests.py")
    >>> testname = py + ":failing_test"
    >>> run(argv=["nosetests", "-v", "--with-color",
    ...           "--with-doctest", "--doctest-extension", ".rst",
    ...           testname],
    ...     plugins=plugins)
    ...     # doctest: +REPORT_NDIFF
    {normal}failing_tests.failing_test{normal}{normal} ... {normal}{magenta}FAIL{normal}
    <BLANKLINE>
    ======================================================================
    {magenta}FAIL{normal}: failing_tests.failing_test
    ----------------------------------------------------------------------
    Traceback (most recent call last):
    {normal}  File "{boldblue}.../case.py{normal}", line {boldred}...{normal}, in {boldcyan}runTest{normal}
    {cyan}    self.test(*self.arg){normal}
    {normal}  File "{boldblue}test-support/failing/failing_tests.py{normal}", line {boldred}5{normal}, in {boldcyan}failing_test{normal}
    {cyan}    assert False{normal}
    {red}AssertionError{normal}
    <BLANKLINE>
    ----------------------------------------------------------------------
    Ran {boldred}1 {normal}test in {green}...{normal} seconds
    {magenta}FAILED{normal} (failures={magenta}1{normal})


A test that raises an error highlights the errors and failures in red.
The test run summary is still in magenta.

    >>> py = os.path.join(directory_with_tests, "failing", "failing_tests.py")
    >>> testname = py + ":erroring_test"
    >>> run(argv=["nosetests", "-v", "--with-color",
    ...           "--with-doctest", "--doctest-extension", ".rst",
    ...           testname],
    ...     plugins=plugins)
    ...     # doctest: +REPORT_NDIFF
    {normal}failing_tests.erroring_test{normal}{normal} ... {normal}{boldred}ERROR{normal}
    <BLANKLINE>
    ======================================================================
    {boldred}ERROR{normal}: failing_tests.erroring_test
    ----------------------------------------------------------------------
    Traceback (most recent call last):
    {normal}  File "{boldblue}unittest.py{normal}", line {boldred}260{normal}, in {boldcyan}run{normal}
    {cyan}    testMethod(){normal}
    {normal}  File "{boldblue}.../case.py{normal}", line {boldred}...{normal}, in {boldcyan}runTest{normal}
    {cyan}    self.test(*self.arg){normal}
    {normal}  File "{boldblue}test-support/failing/failing_tests.py{normal}", line {boldred}2{normal}, in {boldcyan}erroring_test{normal}
    {cyan}    raise Exception(){normal}
    {red}Exception{normal}
    <BLANKLINE>
    ----------------------------------------------------------------------
    Ran {boldred}1 {normal}test in {green}...{normal} seconds
    {magenta}FAILED{normal} (errors={boldred}1{normal})


Passing doctest looks just like any other passing test

    >>> suitepath = os.path.join(directory_with_tests, "passing",
    ...                          "passing_doctest.rst")
    >>> run(argv=["nosetests", "-v", "--with-color",
    ...           "--with-doctest", "--doctest-extension", ".rst",
    ...           suitepath],
    ...     plugins=plugins)
    ...     # doctest: +REPORT_NDIFF
    {normal}Doctest: passing_doctest.rst{normal}{normal} ... {normal}{green}ok{normal}
    <BLANKLINE>
    ----------------------------------------------------------------------
    Ran {green}1 {normal}test in {green}...{normal} seconds
    {green}OK{normal}


Failing doctest

    >>> suitepath = os.path.join(directory_with_tests, "failing",
    ...                          "failing_doctest.rst")
    >>> run(argv=["nosetests", "-v", "--with-color",
    ...           "--with-doctest", "--doctest-extension", ".rst",
    ...           suitepath],
    ...     plugins=plugins)
    ...     # doctest: +REPORT_NDIFF
    {normal}Doctest: failing_doctest.rst{normal}{normal} ... {normal}{magenta}FAIL{normal}
    <BLANKLINE>
    ======================================================================
    {magenta}FAIL{normal}: Doctest: failing_doctest.rst
    ----------------------------------------------------------------------
    Traceback (most recent call last):
    {normal}  File "{boldblue}doctest.py{normal}", line {boldred}2112{normal}, in {boldcyan}runTest{normal}
    {cyan}    raise self.failureException(self.format_failure(new.getvalue())){normal}
    {red}DocTestFailureException: Failed doctest test for failing_doctest.rst{normal}
    {normal}  File "{boldblue}test-support/failing/failing_doctest.rst{normal}", line {boldred}0{normal}
    <BLANKLINE>
    ----------------------------------------------------------------------
    {normal}File "{boldblue}test-support/failing/failing_doctest.rst{normal}", line {boldred}1{normal}, in {boldcyan}failing_doctest.rst{normal}
    Failed example:
    {cyan}    True{normal}
    Expected:
    {green}    False{normal}
    Got:
    {red}    True{normal}
    <BLANKLINE>
    <BLANKLINE>
    ----------------------------------------------------------------------
    Ran {boldred}1 {normal}test in {green}...{normal} seconds
    {magenta}FAILED{normal} (failures={magenta}1{normal})


Failing doctest with REPORT_NDIFF turned on.  The ndiff gets syntax-coloured.

    >>> suitepath = os.path.join(directory_with_tests, "failing",
    ...                          "failing_doctest_with_ndiff.rst")
    >>> run(argv=["nosetests", "-v", "--with-color",
    ...           "--with-doctest", "--doctest-extension", ".rst",
    ...           suitepath],
    ...     plugins=plugins)
    ...     # doctest: +REPORT_NDIFF
    {normal}Doctest: failing_doctest_with_ndiff.rst{normal}{normal} ... {normal}{magenta}FAIL{normal}
    <BLANKLINE>
    ======================================================================
    {magenta}FAIL{normal}: Doctest: failing_doctest_with_ndiff.rst
    ----------------------------------------------------------------------
    Traceback (most recent call last):
    {normal}  File "{boldblue}doctest.py{normal}", line {boldred}2112{normal}, in {boldcyan}runTest{normal}
    {cyan}    raise self.failureException(self.format_failure(new.getvalue())){normal}
    {red}DocTestFailureException: Failed doctest test for failing_doctest_with_ndiff.rst{normal}
    {normal}  File "{boldblue}test-support/failing/failing_doctest_with_ndiff.rst{normal}", line {boldred}0{normal}
    <BLANKLINE>
    ----------------------------------------------------------------------
    {normal}File "{boldblue}test-support/failing/failing_doctest_with_ndiff.rst{normal}", line {boldred}1{normal}, in {boldcyan}failing_doctest_with_ndiff.rst{normal}
    Failed example:
    {cyan}    print "The quick brown fox jumps over the lazy dog."{normal}
    {cyan}        # doctest: +REPORT_NDIFF{normal}
    Differences (ndiff with -expected +actual):
    {green}    - 'The quick brown zox jumps over the spam lazy dog.'{normal}
    {magenta}    ? -                ^                 -----          -{normal}
    {red}    + The quick brown fox jumps over the lazy dog.{normal}
    {magenta}    ?                 ^{normal}
    <BLANKLINE>
    <BLANKLINE>
    ----------------------------------------------------------------------
    Ran {boldred}1 {normal}test in {green}...{normal} seconds
    {magenta}FAILED{normal} (failures={magenta}1{normal})



The --auto-color option will determine if stdout is a terminal, and
only enable colorized output if so.  Of course, stdout is not a
terminal here, so no color will be produced:

    >>> import nose.plugins.plugintest
    >>> nose.plugins.plugintest.run(
    ...     argv=["nosetests", "-v", "--auto-color",
    ...           "--with-doctest", "--doctest-extension", ".rst",
    ...           os.path.join(directory_with_tests, "passing")],
    ...     plugins=plugins)
    ...     # doctest: +REPORT_NDIFF
    Doctest: passing_doctest.rst ... ok
    passing_tests.passing_test_1 ... ok
    passing_tests.passing_test_2 ... ok
    <BLANKLINE>
    ----------------------------------------------------------------------
    Ran 3 tests in ...s
    <BLANKLINE>
    OK


If --with-color or environment variable NOSE_WITH_COLOR have been
previously set (perhaps by a test runner wrapper script), but no
colorized output is desired, the --no-color option will disable
colorized output:

    >>> nose.plugins.plugintest.run(
    ...     env={"NOSE_WITH_COLOR": True},
    ...     argv=["nosetests", "-v", "--with-color", "--no-color",
    ...           "--with-doctest", "--doctest-extension", ".rst",
    ...           os.path.join(directory_with_tests, "passing")],
    ...     plugins=plugins)
    ...     # doctest: +REPORT_NDIFF
    Doctest: passing_doctest.rst ... ok
    passing_tests.passing_test_1 ... ok
    passing_tests.passing_test_2 ... ok
    <BLANKLINE>
    ----------------------------------------------------------------------
    Ran 3 tests in ...s
    <BLANKLINE>
    OK


Clean up:

    >>> sys.stdout = real_stdout
