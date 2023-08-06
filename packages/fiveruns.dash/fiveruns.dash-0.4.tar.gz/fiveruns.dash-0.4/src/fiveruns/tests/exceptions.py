from fiveruns import dash
from mock import Mock
import unittest
import traceback
from StringIO import StringIO

class RecorderTest(unittest.TestCase):
    def setUp(self):
        session = Mock(spec=dash.session.Reporter)
        self.recorder = dash.exceptions.Recorder(session)
    
    def tearDown(self):
        pass

    def testRecord(self):
        def dummyException():
            raise Exception('Dummy Exception')
   
        loops_to_do = 2
        cnt = 0
        name = None
        msg = None
        backtrace = None
        sample_arg = {'one': 1, 'two': 2}
        sample_test = {}
        for k,v in sample_arg.iteritems():
            sample_test[str(k)] = str(v)

        while cnt < loops_to_do:
            cnt += 1
            try:
                dummyException()
            except Exception, e:
                name = type(e).__name__
                msg = '\n'.join(e.args)
                backtrace = StringIO()
                traceback.print_exc(file=backtrace)
                self.recorder.record(e, sample_arg)

            key = (name, backtrace.getvalue())
            data = self.recorder.data
            self.assert_(key in data)
            self.assert_('sample' in data[key])
            self.assertEqual(data[key]['sample'], sample_test)
            self.assert_('backtrace' in data[key])
            self.assertEqual(data[key]['backtrace'], backtrace.getvalue())
            self.assert_('message' in data[key])
            self.assertEqual(data[key]['message'], msg)
            self.assert_('total' in data[key])
            self.assertEqual(data[key]['total'], cnt)
            self.assert_('name' in data[key])
            self.assertEqual(data[key]['name'], name)
