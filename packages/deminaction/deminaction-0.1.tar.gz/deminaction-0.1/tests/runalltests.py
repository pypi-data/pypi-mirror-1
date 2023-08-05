# this isn't the most serious test runner, but it works well enough

import sys
import unittest
import doctest

from deminaction.tests import supporters, campaigns, donations, events, customfields
from deminaction.tests import badxml

tests = (
    doctest.DocTestSuite(supporters),
    doctest.DocTestSuite(customfields),
    doctest.DocTestSuite(campaigns),
    doctest.DocTestSuite(donations),
    doctest.DocTestSuite(events),
    doctest.DocTestSuite(badxml),
    )

suite = unittest.TestSuite()
suite.addTests(tests)

runner = unittest.TextTestRunner()
result = runner.run(suite)

bad = len(result.failures) + len(result.errors)

if bad:
    sys.exit(1)
