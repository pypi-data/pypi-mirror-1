import unittest
from protocol import (PayloadTest,
                      InfoPayloadTest,
                      DataPayloadTest,
                      OtherPayloadTests,
                      TransportTests)
from configuration import ConfigurationTest
from exceptions import RecorderTest
from session import ReporterTest
from metrics import (CalculationTest,
                     MetricTest,
                     CounterMetricTest,
                     TimeMetricTest,
                     MetricSettingTest)
from recipe import RecipeTest

def test_suite():
    tests = [PayloadTest,
             InfoPayloadTest,
             DataPayloadTest,
             OtherPayloadTests,
             TransportTests,
             ConfigurationTest,
             RecorderTest,
             ReporterTest,
             CalculationTest,
             MetricTest,
             CounterMetricTest,
             TimeMetricTest,
             MetricSettingTest,
             RecipeTest]
    individual_suites = [unittest.makeSuite(test) for test in tests]
    
    def reduce_func(suite, test):
        suite.addTest(test)
        return suite
    return reduce(reduce_func, individual_suites)
