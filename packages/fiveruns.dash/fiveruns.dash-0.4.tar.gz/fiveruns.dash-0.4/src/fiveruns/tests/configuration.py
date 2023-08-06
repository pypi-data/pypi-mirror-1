from fiveruns import dash
from mock import Mock
import unittest

class ConfigurationTest(unittest.TestCase):
    def setUp(self):
        self.config = dash.configure(app_token='ABC123')
        reporter = Mock(spec=dash.session.Reporter)
        self.config.reporter = reporter
        
        def testWithException():
            raise Exception("Test Exception")
        self.testWithException = self.config.add_exceptions_from()(testWithException)
    
    def tearDown(self):
        pass

    def testAddExceptionsFromWithException(self):
        try:
            self.testWithException()
        except:
            pass
        else:
            fail('Expected an exception to be caught')
        self.assertEqual(True, self.config.reporter.add_exception.called)
        
    def testAddExceptionsFromWithBadReporter(self):
        reporter = Mock()
        reporter.add_exception.return_value = None
        except_str = 'Mock Reporter threw and exception'
        def reporter_exception():
            raise Exception(except_str)
        reporter.add_exception.side_effect = reporter_exception
        self.config.reporter = reporter
        try:
            self.testWithException()
        except Exception, e:
            self.assert_(str(e) != except_str)
        self.assertEqual(True, self.config.reporter.add_exception.called)

    def testAddExceptionsFromWithReturnValue(self):
        RETVAL = 1
        def testWithRetval():
            return RETVAL
        testWithRetval = self.config.add_exceptions_from()(testWithRetval)
        testval = testWithRetval()
        self.assertEqual(testval, RETVAL)
        self.assertEqual(False, self.config.reporter.add_exception.called)

    def testAddExceptionsFromWithArgs(self):
        args = (1,2,3)
        kwargs = {'dash': 1, 'tuneup': 2}
        testWithArgs = Mock(return_value = None)
        decoratedTestWithArgs = self.config.add_exceptions_from()(testWithArgs)

        decoratedTestWithArgs(*args, **kwargs)
        self.assertEqual( (args, kwargs), testWithArgs.call_args )

    def testInstrument(self):
        metric1 = Mock()
        metric1._instrument.return_value = None
        metric2 = Mock()
        metric2._instrument.return_value = None
        metrics = Mock()
        metrics.values.return_value = [metric1, metric2]

        self.config.metrics = metrics
        self.config.instrument()
        self.assertEqual(True, metric1._instrument.called)
        self.assertEqual(True, metric2._instrument.called)
