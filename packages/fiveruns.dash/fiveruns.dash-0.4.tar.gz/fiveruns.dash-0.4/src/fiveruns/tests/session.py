from fiveruns import dash
from mock import Mock, patch
import unittest
import time

MOCK_TIME = Mock(return_value=111111)
class ReporterTest(unittest.TestCase):
    def setUp(self):
        config = dash.configure(app_token='ABC123')
        self.reporter = spec=dash.session.Reporter(config)

        self.original_info_send = dash.protocol.InfoPayload.send
        self.mock_info = 'mock info'
        patch('fiveruns.dash.protocol.InfoPayload.send', Mock(return_value=self.mock_info))
        
    def tearDown(self):
        patch('fiveruns.dash.protocol.InfoPayload.send', self.original_info_send)

    def testAddException(self):
        self.reporter.exception_recorder = Mock()
        self.reporter.exception_recorder.record.return_value = None

        self.reporter.add_exception(None)
        self.assertEqual(True, self.reporter.exception_recorder.record.called)

    def testPrivateReportData(self):
        orig_DataPayload = dash.protocol.DataPayload
        patch('fiveruns.dash.protocol.DataPayload', Mock(spec=dash.protocol.DataPayload))
        dash.protocol.DataPayload.send = Mock(return_value='mock data')
        self.reporter.reported_info = True
        self.reporter._report_data()

        self.assertEqual(self.reporter.last_report, MOCK_TIME())
        self.failUnless(dash.protocol.DataPayload.send.called)
        patch('fiveruns.dash.protocol.DataPayload', dash.protocol.DataPayload)
    testPrivateReportData = patch('time.time', MOCK_TIME)(testPrivateReportData)

    def testPrivateIsReady(self):
        self.reporter.last_report = 2
        self.failIf(self.reporter._is_ready())

        self.reporter.last_report = 1
        self.failIf(self.reporter._is_ready())
        
        self.reporter.last_report = 0
        self.failUnless(self.reporter._is_ready())
    testPrivateIsReady = patch('time.time', Mock(return_value=61))(testPrivateIsReady)
