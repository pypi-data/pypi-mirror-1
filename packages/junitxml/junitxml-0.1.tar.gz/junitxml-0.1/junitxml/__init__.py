#
#  junitxml: extensions to Python unittest to get output junitxml
#  Copyright (C) 2009 Robert Collins <robertc@robertcollins.net>
#
#  Copying permitted under the LGPL-3 licence, included with this library.

"""unittest compatible JUnit XML output."""


import datetime
import unittest
from xml.sax.saxutils import escape


def test_suite():
    import junitxml.tests
    return junitxml.tests.test_suite()


class JUnitXmlResult(unittest.TestResult):
    """A TestResult which outputs JUnit compatible XML."""
    
    def __init__(self, stream):
        """Create a JUnitXmlResult.

        :param stream: A stream to write results to. Note that due to the
            nature of JUnit XML output, nnothing will be written to the stream
            until stopTestRun() is called.
        """
        super(JUnitXmlResult, self).__init__()
        self._stream = stream
        self._results = []
        self._set_time = None
        self._test_start = None
        self._run_start = None

    def _super(self):
        return super(JUnitXmlResult, self)

    def startTestRun(self):
        """Start a test run."""
        self._run_start = self._now()

    def _now(self):
        if self._set_time is not None:
            return self._set_time
        else:
            return datetime.datetime.utcnow()

    def time(self, a_datetime):
        self._set_time = a_datetime

    def startTest(self, test):
        self._test_start = self._now()

    def _duration(self, from_datetime):
        delta = self._now() - from_datetime
        seconds = delta.days * 3600*24 + delta.seconds
        return seconds + 0.000001 * delta.microseconds

    def _test_case_string(self, test):
        duration = self._duration(self._test_start)
        prefix_suffix = test.id().rsplit('.', 1)
        if len(prefix_suffix) == 1:
            classname = ""
            name = prefix_suffix
        else:
            classname = prefix_suffix[0]
            name = prefix_suffix[1]
        self._results.append('<testcase classname="%s" name="%s" '
            'time="%0.3f"' % (escape(classname), escape(name), duration))

    def stopTestRun(self):
        """Stop a test run.

        This allows JUnitXmlResult to output the XML representation of the test
        run.
        """
        duration = self._duration(self._run_start)
        self._stream.write('<testsuite errors="%d" failures="%d" name="" tests="0" time="%0.3f">\n' % (len(self.errors), len(self.failures), duration))
        self._stream.write(''.join(self._results))
        self._stream.write('</testsuite>\n')

    def addError(self, test, error):
        self._super().addError(test, error)
        self._test_case_string(test)
        self._results.append('>\n')
        self._results.append('<error type="%s.%s">%s</error>\n</testcase>\n'% (escape(error[0].__module__), escape(error[0].__name__), escape(self._exc_info_to_string(error, test))))

    def addFailure(self, test, error):
        self._super().addFailure(test, error)
        self._test_case_string(test)
        self._results.append('>\n')
        self._results.append('<failure type="%s.%s">%s</failure>\n</testcase>\n'% (escape(error[0].__module__), escape(error[0].__name__), escape(self._exc_info_to_string(error, test))))

    def addSuccess(self, test):
        self._super().addSuccess(test)
        self._test_case_string(test)
        self._results.append(' />\n')

    def addSkip(self, test, reason):
        self._super().addSkip(test, reason)
        self._test_case_string(test)
        self._results.append('>\n')
        self._results.append('<skip type="%s.%s">%s</skip>\n</testcase>\n'% (escape(error[0].__module__), escape(error[0].__name__), escape(reason)))

    def addUnexpectedSuccess(self, test):
        self._super().addUnexpectedSuccess(test, error)
        self._test_case_string(test)
        self._results.append(' />\n')

    def addExpectedFailure(self, test, error):
        self._super().addExpectedFailure(test, error)
        self._test_case_string(test)
        self._results.append('>\n')
        self._results.append('<failure type="%s.%s">%s</failure>\n</testcase>\n'% (escape(error[0].__module__), escape(error[0].__name__), escape(self._exc_info_to_string(error, test))))

