from dm.testunit import ApplicationTestSuite
from dm.testunit import TestCase
from desire.builder import ApplicationBuilder

class TestCase(TestCase):
    "Base class for desire TestCases."

class ApplicationTestSuite(ApplicationTestSuite):
    appBuilderClass = ApplicationBuilder

