from fiveruns import dash
from mock import Mock, patch, patch_object
import unittest
import helper
import os
import sys

def mock_send(status, reason, body):
    mocked_send = Mock()
    mocked_send.return_value = (status, reason, body)
    return mocked_send

class PayloadTest(unittest.TestCase):
    def setUp(self):
        dash.recipes.registry.clear()
        self.config = dash.configure(app_token='ABC123')
    
    def tearDown(self):
        pass

    def testPayloadSendSuccessful(self):
        payload = dash.protocol.InfoPayload(self.config)
        self.assertEqual(True, payload.send())
    testPayloadSendSuccessful = patch('fiveruns.dash.protocol.send', mock_send(201, 'Created', 'InfoPayload: Successful body'))(testPayloadSendSuccessful)

    def testPayloadSendFailed(self):
        payload = dash.protocol.InfoPayload(self.config)
        self.assertEqual(False, payload.send())
    testPayloadSendFailed = patch('fiveruns.dash.protocol.send', mock_send(404, 'Not Found', 'InfoPayload: This is the body of a failed Payload Send Request'))(testPayloadSendFailed)
    
    def testPayloadSendUnknownError(self):
        payload = dash.protocol.InfoPayload(self.config)
        self.assertEqual(False, payload.send())
    testPayloadSendUnknownError = patch('fiveruns.dash.protocol.send', mock_send(500, 'Server Error','InfoPayload: This is the body of an unknown error with a Send Request'))(testPayloadSendUnknownError)

    def testURL(self):
        dash.protocol.Payload._extract_data = Mock()
        payload = dash.protocol.Payload(self.config)
        
        self.assert_(payload.url() == 'https://dash-collector.fiveruns.com')
        
        update_url = 'https://dash-collector-update.fiveruns.com'
        os.environ['DASH_UPDATE'] = update_url
        self.assert_(payload.url() == update_url)
        

    def testValid(self):
        dash.protocol.Payload._extract_data = Mock()
        payload = dash.protocol.Payload(self.config)
        payload._extract_data = Mock()

        validation = Mock()
        validation.return_value = True
        dash.protocol.Payload.validations = [validation]
        
        self.assertEqual(True, payload.valid())
        self.assertEqual(True, validation.called)

        validation.reset_mock()
        validation.return_value = False
        dash.protocol.Payload.validations = [validation]
        
        self.assertEqual(False, payload.valid())
        self.assertEqual(True, validation.called)

class InfoPayloadTest(unittest.TestCase):
    def setUp(self):
        dash.recipes.registry.clear()
        self.app_token = 'ABC123'
        self.config = dash.configure(app_token=self.app_token)

    def tearDown(self):
        pass

    def testPath(self):
        payload = dash.protocol.InfoPayload(self.config)
        self.assertEqual('/apps/%s/processes.json' % self.app_token, payload.path())
    
    def testDataMember(self):
        self.config.metrics = Mock()
        self.config.metrics.values = Mock()
        metric1_name = "m1 name"
        metric1_url = "http://m1.fiveruns.com"
        metric1 = Mock()
        metric1.metadata = Mock()
        metric1.metadata.return_value = {'recipe_name': metric1_name,
                                         'recipe_url': metric1_url} 
       
        metric2_name = "m2 name"
        metric2_url = "http://m2.fiveruns.com"
        metric2 = Mock()
        metric2.metadata = Mock()
        metric2.metadata.return_value = {'recipe_name':metric2_name,
                                         'recipe_url': metric2_url}

        self.config.metrics.values.return_value = [metric1, metric2]
        payload = dash.protocol.InfoPayload(self.config)
        
        recipe1 = {'url': metric1_url, 'name': metric1_name}
        recipe2 = {'url': metric2_url, 'name': metric2_name}
        metric1_info = metric1.metadata()
        metric2_info = metric2.metadata()
        
        self.assertEqual(True, 'recipes' in payload.data)
        self.assertEqual(True, recipe1 in payload.data['recipes'])
        self.assertEqual(True, recipe2 in payload.data['recipes'])
        self.assertEqual(True, 'metric_infos' in payload.data)
        self.assertEqual(True, metric1_info in payload.data['metric_infos'])
        self.assertEqual(True, metric2_info in payload.data['metric_infos'])

class DataPayloadTest(unittest.TestCase):
    def setUp(self):
        dash.recipes.registry.clear()
        self.app_token = 'ABC123'
        self.config = dash.configure(app_token=self.app_token)

    def tearDown(self):
        pass

    def testPath(self):
        payload = dash.protocol.DataPayload(self.config)
        self.assertEqual('/apps/%s/metrics.json' % self.app_token, payload.path())
    

    def testDataMember(self):
        id = 1
        metric = Mock()
        metric.name = "Metric %s" % id
        metric.help_text = "Metric %s help text" % id
        metric.unit = "Metric %s unit" % id
        metric.data_type = "Metric %s data type" % id
        metric.description = "Metric %s description" % id
        metric.recipe_name = "Metric %s recipe_name" % id
        metric.recipe_url = "http://metric%s.fiveruns.com" % id
        metric.virtual = False
        metric.values = Mock()
        metric.values.return_value = map(lambda x: x*id, [1,2,3])

        expected_data= {
            'name': metric.name,
            'data_type': metric.data_type,
            'recipe_name': metric.recipe_name,
            'values': metric.values(),
            'recipe_url': metric.recipe_url,
            'help_text': metric.help_text,
            'unit': metric.unit,
            'description': metric.description
        }

        self.config.metrics = Mock()
        self.config.metrics.iteritems = Mock()
        self.config.metrics.iteritems.return_value = [('metric', metric)]
        
        payload = dash.protocol.DataPayload(self.config)
        test_data = payload.data[0]
        for k,v in expected_data.iteritems():
            self.assert_(v == test_data[k])


class OtherPayloadTests(unittest.TestCase):
    def setUp(self):
        dash.recipes.registry.clear()
        self.app_token = 'ABC123'
        self.config = dash.configure(app_token=self.app_token)

    def testOtherPayloadPaths(self):
        path_tests = [(dash.protocol.PingPayload(self.config), '/apps/%s/ping' % self.app_token),
                      (dash.protocol.TracePayload(self.config), '/apps/%s/traces.json' % self.app_token),
                      (dash.protocol.ExceptionsPayload(self.config), '/apps/%s/exceptions' % self.app_token)]

        for path_test in path_tests:
            self.assert_(path_test[0].path() == path_test[1])


resp_status = 201
resp_reason = 'reason'
resp_body = 'body'
exc_info = 'Bad Request'

def mock_connector(throw_exception=False):
    response = Mock()
    response.status = resp_status
    response.reason = resp_reason
    response.read.return_value = resp_body

    connection = Mock()
    connection.request.return_value = None
    if throw_exception:
        def an_exception(*arg, **kwargs):
            raise Exception(exc_info)
        connection.request.side_effect = an_exception
    connection.getresponse.return_value = response

    
    connector = Mock()
    connector.return_value = connection
    return connector

http_conn = mock_connector()
https_conn = mock_connector()
except_conn = mock_connector(throw_exception=True)

class TransportTests(unittest.TestCase):
    def testSendFunction(self):
        #Ensure HTTP is used
        urlparts = ['http', 'dash.fiveruns.com']
        selector = 'http://dash.fiveruns.com'
        fields = []
        files = []

        status, reason, body = dash.protocol.send(urlparts, selector, fields, files)
        self.assertEqual(True, http_conn.called)
        self.assertEqual(True, http_conn().request.called)
        self.assertEqual(True, http_conn().getresponse.called)
        self.assertEqual(status, resp_status)
        self.assertEqual(reason, resp_reason)
        self.assertEqual(body, resp_body)

        #Ensure HTTPS is used
        urlparts = ['https', 'dash.fiveruns.com']
        selector = 'https://dash.fiveruns.com'
        status, reason, body = dash.protocol.send(urlparts, selector, fields, files)
        self.assertEqual(True, http_conn.called)
        self.assertEqual(True, https_conn().request.called)
        self.assertEqual(True, https_conn().getresponse.called)
        self.assertEqual(status, resp_status)
        self.assertEqual(reason, resp_reason)
        self.assertEqual(body, resp_body)
    testSendFunction = patch('fiveruns.dash.protocol.connections', 
                             {'http': http_conn, 'https': https_conn})(testSendFunction)

    def testSendFunctionException(self):
        urlparts = ['http', 'dash.fiveruns.com']
        selector = 'http://dash.fiveruns.com'
        fields = []
        files = []

        #Ensure exception caught
        status, reason, body = dash.protocol.send(urlparts, selector, fields, files)
        self.assertEqual(True, http_conn.called)
        self.assertEqual(True, https_conn().request.called)
        self.assertEqual(False, status)
        self.assertEqual(reason, exc_info)
        self.assertEqual(body, None)
    testSendFunctionException = patch('fiveruns.dash.protocol.connections', 
                                      {'http': except_conn})(testSendFunctionException)

    def testEncodeFunction(self):
        '''
        Test of fiveruns.dash.protocol.encode
        '''
        #not sure how to test this other than just writing the entire function as is...
        pass
