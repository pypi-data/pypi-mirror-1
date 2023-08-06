#
#  junitxml: extensions to Python unittest to get output junitxml
#  Copyright (C) 2009 Robert Collins <robertc@robertcollins.net>
#
#  Copying permitted under the LGPL-3 licence, included with this library.


from cStringIO import StringIO
import re
import unittest

import junitxml

class TestImports(unittest.TestCase):

    def test_result(self):
        from junitxml import JUnitXmlResult


class TestJUnitXmlResult__init__(unittest.TestCase):

    def test_with_stream(self):
        result = junitxml.JUnitXmlResult(StringIO())


class TestJUnitXmlResult(unittest.TestCase):

    def setUp(self):
        self.output = StringIO()
        self.result = junitxml.JUnitXmlResult(self.output)

    def get_output(self):
        output = self.output.getvalue()
        # Collapse detailed regions into specific strings we can match on
        return re.sub(r'(?s)<failure (.*?)>.*?</failure>',
            r'<failure \1>failure</failure>', re.sub(
            r'(?s)<error (.*?)>.*?</error>', r'<error \1>error</error>',
            re.sub(r'time="\d+\.\d+"', 'time="0.000"', output)))

    def test_startTestRun_no_output(self):
        # startTestRun doesn't output anything, because JUnit wants an up-front
        # summary.
        self.result.startTestRun()
        self.assertEqual('', self.get_output())

    def test_stopTestRun_outputs(self):
        # When stopTestRun is called, everything is output.
        self.result.startTestRun()
        self.result.stopTestRun()
        self.assertEqual("""<testsuite errors="0" failures="0" name="" tests="0" time="0.000">
</testsuite>
""", self.get_output())

    def test_erroring_test(self):
        class Errors(unittest.TestCase):
            def test_me(self):
                1/0
        self.result.startTestRun()
        Errors("test_me").run(self.result)
        self.result.stopTestRun()
        self.assertEqual("""<testsuite errors="1" failures="0" name="" tests="0" time="0.000">
<testcase classname="junitxml.tests.test_junitxml.Errors" name="test_me" time="0.000">
<error type="exceptions.ZeroDivisionError">error</error>
</testcase>
</testsuite>
""", self.get_output())

    def test_failing_test(self):
        class Fails(unittest.TestCase):
            def test_me(self):
                self.fail()
        self.result.startTestRun()
        Fails("test_me").run(self.result)
        self.result.stopTestRun()
        self.assertEqual("""<testsuite errors="0" failures="1" name="" tests="0" time="0.000">
<testcase classname="junitxml.tests.test_junitxml.Fails" name="test_me" time="0.000">
<failure type="exceptions.AssertionError">failure</failure>
</testcase>
</testsuite>
""", self.get_output())

    def test_successful_test(self):
        class Passes(unittest.TestCase):
            def test_me(self):
                pass
        self.result.startTestRun()
        Passes("test_me").run(self.result)
        self.result.stopTestRun()
        self.assertEqual("""<testsuite errors="0" failures="0" name="" tests="0" time="0.000">
<testcase classname="junitxml.tests.test_junitxml.Passes" name="test_me" time="0.000" />
</testsuite>
""", self.get_output())

    def test_skip_test(self):
        class Skips(unittest.TestCase):
            def test_me(self):
                try:
                    self.skipTest("yo")
                except AttributeError:
                    # Older python - degrade to a pass
                    pass
        self.result.startTestRun()
        Skips("test_me").run(self.result)
        self.result.stopTestRun()
        output = self.get_output()
        expected = """<testsuite errors="0" failures="0" name="" tests="0" time="0.000">
<testcase classname="junitxml.tests.test_junitxml.Skips" name="test_me" time="0.000">
<skip type="unittest.SkipTest">yo</skip>
</testcase>
</testsuite>
"""
        expected_old = """<testsuite errors="0" failures="0" name="" tests="0" time="0.000">
<testcase classname="junitxml.tests.test_junitxml.Skips" name="test_me" time="0.000" />
</testsuite>
"""
        if output != expected_old:
            self.assertEqual(expected, output)

    def test_unexpected_success_test(self):
        class Succeeds(unittest.TestCase):
            def test_me(self):
                try:
                    unittest.expectedFailure(lambda:None)()
                except AttributeError:
                    # Older python - degrade to a pass
                    pass
        self.result.startTestRun()
        Succeeds("test_me").run(self.result)
        self.result.stopTestRun()
        self.assertEqual("""<testsuite errors="0" failures="0" name="" tests="0" time="0.000">
<testcase classname="junitxml.tests.test_junitxml.Succeeds" name="test_me" time="0.000" />
</testsuite>
""", self.get_output())

    def test_expected_failure_test(self):
        class ExpectedFail(unittest.TestCase):
            def test_me(self):
                try:
                    unittest.expectedFailure(lambda:None)()
                except AttributeError:
                    # Older python - degrade to a fail
                    self.fail("fail")
        self.result.startTestRun()
        ExpectedFail("test_me").run(self.result)
        self.result.stopTestRun()
        output = self.get_output()
        expected = """<testsuite errors="0" failures="1" name="" tests="0" time="0.000">
<testcase classname="junitxml.tests.test_junitxml.ExpectedFail" name="test_me" time="0.000">
<failure type="unittest._ExpectedFailure">failure</failure>
</testcase>
</testsuite>
"""
        expected_old = """<testsuite errors="0" failures="1" name="" tests="0" time="0.000">
<testcase classname="junitxml.tests.test_junitxml.ExpectedFail" name="test_me" time="0.000">
<failure type="exceptions.AssertionError">failure</failure>
</testcase>
</testsuite>
"""
        if output != expected_old:
            self.assertEqual(expected, output)
