from fiveruns import dash
from mock import Mock, patch
import unittest
import time

class CalculationTest(unittest.TestCase):
    def setUp(self):
        pass
    
    def tearDown(self):
        pass

    def testRun(self):
        v1 = 1
        v2 = 2
        def operation(value1, value2):
            return value1 + value2
        fields = []
        calc = dash.metrics.Calculation(operation, *fields)
        test_val = calc.run(*[v1, v2])
        self.assertEqual(test_val, operation(v1,v2))

class MetricTest(unittest.TestCase):
    def setUp(self):
        dash.metrics.Metric._data_type = Mock(return_value=None)
        dash.metrics.Metric._validate = Mock(return_value=None)
        self.metric = dash.metrics.Metric('metric', 'a test metric')
        self.metric.lock.acquire = Mock(return_value=None)
        self.metric.lock.release = Mock(return_value=None)

    def tearDown(self):
        pass

    def testVirtual(self):
        self.failIf(self.metric.virtual)
        self.metric.calculation = Mock()
        self.failUnless(self.metric.virtual)

    def testCalculate(self):
        data = []
        self.failIf(self.metric.virtual)
        self.assertEqual(self.metric.calculate(data), [])

        def operation(*args):
            return reduce(lambda x,y: x+y, args)

        field1 = 'f1'
        field2 = 'f2'
        value1 = 1
        value2 = 2
        context = ''
        self.metric.recipe_name = 'fake recipe'
        self.metric.recipe_url = 'http://fake.fiveruns.com'
        self.metric.calculation = dash.metrics.Calculation(operation, *[field1, field2])
        data_key1 = (field1, self.metric.recipe_name, self.metric.recipe_url)
        data_key2 = (field2, self.metric.recipe_name, self.metric.recipe_url)
        data = {data_key1: {'values':[{'context': context, 'value': value1}]},
                data_key2: {'values':[{'context': context, 'value': value2}]}}
        test_results = self.metric.calculate(data)
        
        self.failIf(len(test_results) == 0)
        self.failUnless('value' in test_results[0])
        self.failUnless('context' in test_results[0])
        self.assertEqual(test_results[0]['value'], operation(*[value1, value2]))
        self.assertEqual(test_results[0]['context'], context)

    def testValues(self):
        self.failIf(self.metric.virtual)
        self.metric._snapshot = Mock(return_value='snapshot')
        self.metric.values()
        self.failUnless(self.metric._snapshot.called)

    def testMetadata(self):
        self.metric.data_type = 'datatype'
        self.metric.recipe_name = 'recipe name'
        self.metric.recipe_url = 'http://dash.fiveruns.com'
        self.metric.help_text = 'help text'
        self.metric.unit = 'unit'
        self.metric._data_type = Mock(return_value=self.metric.data_type)
        
        keys = ['name', 'unit', 'description', 'help_text', 'recipe_name', 'recipe_url', 'data_type']
        keys.sort()
        test_metadata = self.metric.metadata()
        test_keys = test_metadata.keys()
        test_keys.sort()
        self.failUnless(keys == test_keys)

        for k in keys:
            self.failUnless(self.metric.__dict__[k] == test_metadata[k])

    def testPrivateWrapper(self):
        mock_key = 'container'
        mock_value = 1
        mock_return = {mock_key: mock_value}
        mock_func = Mock(return_value=mock_return)

        self.metric._wrapper(mock_func)
        self.metric._record()
        self.failUnless(mock_func.called)
        self.failUnless(self.metric.lock.acquire.called)
        self.failUnless(self.metric.lock.release.called)
        self.failUnless(self.metric.containers[mock_key] == mock_value)

    def testPrivateSnapshot(self):
        keys = ['container1', 'container2']
        values = [1,2]
        self.metric.containers = dict(zip(keys,values))
        test_values = self.metric._snapshot()
        self.failUnless(len(test_values) == len(values))
        for tv in test_values:
            self.failUnless(tv in values)
        self.failUnless(len(self.metric.containers.keys()) == 0)
        self.failUnless(self.metric.lock.acquire.called)
        self.failUnless(self.metric.lock.release.called)

class CounterMetricTest(unittest.TestCase):
    def setUp(self):
        dash.metrics.Metric._data_type = Mock(return_value=None)
        dash.metrics.Metric._validate = Mock(return_value=None)
        self.metric = dash.metrics.CounterMetric('counter_metric', 'a test counter metric')
        self.metric.lock.acquire = Mock(return_value=None)
        self.metric.lock.release = Mock(return_value=None)

    def tearDown(self):
        pass

    def testValidate(self):
        self.failUnless(self.metric._validate() == None)
    
    def testWrapper(self):
        mock_return = "mock return"
        mock_func = Mock(return_value=mock_return)
        args = (1,2,3)
        kwargs = {'four': 4, 'five': 5, 'six': 6}

        decorated_func = self.metric._wrapper(mock_func)
        retval = decorated_func(*args, **kwargs)

        self.failUnless(mock_func.called)
        self.failUnless(retval == mock_return)
        self.failUnless(mock_func.call_args == (args, kwargs))
        self.failUnless(self.metric.lock.acquire.called)
        self.failUnless(self.metric.lock.release.called)

    def testDataType(self):
        self.failUnless(self.metric._data_type() == 'counter')


    
class TimeMetricTest(unittest.TestCase):
    def setUp(self):
        dash.metrics.Metric._data_type = Mock(return_value=None)
        dash.metrics.Metric._validate = Mock(return_value=None)
        self.metric = dash.metrics.TimeMetric('time_metric', 'a test time metric')
        self.metric.lock.acquire = Mock(return_value=None)
        self.metric.lock.release = Mock(return_value=None)

    def tearDown(self):
        pass

    def testValidate(self):
        self.failUnless(self.metric._validate() == None)
        self.metric.calculation = Mock()
        self.failUnless(self.metric._validate() == True)

    def testDefaultContainerFor(self):
        context = None
        container = self.metric._default_container_for(context)
        self.failUnless('context' in container)
        self.failUnless(container['context'] == context)
        self.failUnless('invocations' in container)
        self.failUnless(container['invocations'] == 0)
        self.failUnless('value' in container)
        self.failUnless(container['value'] == 0)

    
    TIME_MARK = []
    def my_time(timeFunc):
        def decorated_time():
            TimeMetricTest.TIME_MARK.append(timeFunc())
            return TimeMetricTest.TIME_MARK[-1]
        return decorated_time

    def testWrapper(self):
        mock_return = "mock return"
        mock_func = Mock(return_value=mock_return)
        args = (1,2,3)
        kwargs = {'four': 4, 'five': 5, 'six': 6}

        decorated_func = self.metric._wrapper(mock_func)
        retval = decorated_func(*args, **kwargs)

        self.failUnless(mock_func.called)
        self.failUnless(retval == mock_return)
        self.failUnless(mock_func.call_args == (args, kwargs))
        
        container = self.metric._container_for_context(None)
        self.failUnless('value' in container)
        self.failUnless(container['value'] == (TimeMetricTest.TIME_MARK[1]-TimeMetricTest.TIME_MARK[0]))
        self.failUnless('invocations' in container)
        self.failUnless(container['invocations'] == 1)
        self.failUnless(self.metric.lock.acquire.called)
        self.failUnless(self.metric.lock.release.called)
    testWrapper = patch('time.time', my_time(time.time))(testWrapper)

    def testDataType(self):
        self.failUnless(self.metric._data_type() == 'time')

class AbsoluteMetricTest(unittest.TestCase):
    def setUp(self):
        dash.metrics.Metric._data_type = Mock(return_value=None)
        dash.metrics.Metric._validate = Mock(return_value=None)
        self.metric = dash.metrics.AbsoluteMetric('absolute_metric', 'a test absolute metric')

    def tearDown(self):
        pass

    def testValidate(self):
        self.failUnless(self.metric._validate() == None)
        self.metric.calculation = Mock()
        self.failUnless(self.metric._validate() == True)

    def testValues(self):
        self.metric._record = Mock(return_value=None)
        snapshot_return = 'snapshot'
        self.metric._snapshot = Mock(return_value=snapshot_return)
        retval = self.metric.values()
        self.failUnless(retval == snapshot_return)
        self.failUnless(self.metric._record.called)
        self.failUnless(self.metric._snapshot.called)
        
    def testDataType(self):
        self.failUnless(self.metric._data_type() == 'absolute')


class PercentageMetricTest(unittest.TestCase):
    def setUp(self):
        dash.metrics.Metric._data_type = Mock(return_value=None)
        dash.metrics.Metric._validate = Mock(return_value=None)
        self.metric = dash.metrics.PercentageMetric('percentage_metric', 'a test percentage metric')

    def tearDown(self):
        pass

    def testValidate(self):
        self.failUnless(self.metric._validate() == None)
        self.metric.calculation = Mock()
        self.failUnless(self.metric._validate() == True)

    def testValues(self):
        self.metric._record = Mock(return_value=None)
        snapshot_return = 'snapshot'
        self.metric._snapshot = Mock(return_value=snapshot_return)
        retval = self.metric.values()
        self.failUnless(retval == snapshot_return)
        self.failUnless(self.metric._record.called)
        self.failUnless(self.metric._snapshot.called)
        
    def testDataType(self):
        self.failUnless(self.metric._data_type() == 'percentage')

class MetricSettingTest(unittest.TestCase):
    def setUp(self):
        self.setting = dash.metrics.MetricSetting()

    def tearDown(self):
        pass

    def testTime(self):
        name = 'time_metric'
        recipe_name = 'recipe'
        recipe_url = 'http://dash.fiveruns.com'
        desc = 'a description'
        kwargs = {'recipe_name': recipe_name, 'recipe_url': recipe_url}
        retval = self.setting.time(name, desc, **kwargs)
        self.failUnless((name, recipe_name, recipe_url) in self.setting.metrics)
        self.failUnless(retval.im_class == dash.metrics.TimeMetric)
    
    def testCounter(self):
        name = 'counter_metric'
        recipe_name = 'recipe'
        recipe_url = 'http://dash.fiveruns.com'
        desc = 'a description'
        kwargs = {'recipe_name': recipe_name, 'recipe_url': recipe_url}
        retval = self.setting.counter(name, desc, **kwargs)
        self.failUnless((name, recipe_name, recipe_url) in self.setting.metrics)
        self.failUnless(retval.im_class == dash.metrics.CounterMetric)

    def testAbsolute(self):
        name = 'absolute_metric'
        recipe_name = 'recipe'
        recipe_url = 'http://dash.fiveruns.com'
        desc = 'a description'
        kwargs = {'recipe_name': recipe_name, 'recipe_url': recipe_url}
        retval = self.setting.absolute(name, desc, **kwargs)
        self.failUnless((name, recipe_name, recipe_url) in self.setting.metrics)
        self.failUnless(retval.im_class == dash.metrics.AbsoluteMetric)
    
    def testPercentage(self):
        name = 'percentage_metric'
        recipe_name = 'recipe'
        recipe_url = 'http://dash.fiveruns.com'
        desc = 'a description'
        kwargs = {'recipe_name': recipe_name, 'recipe_url': recipe_url}
        retval = self.setting.percentage(name, desc, **kwargs)
        self.failUnless((name, recipe_name, recipe_url) in self.setting.metrics)
        self.failUnless(retval.im_class == dash.metrics.PercentageMetric)

    METRIC_KEY = 'metric'
    METRIC_VALUE = 1
    def mock_find(*args, **kwargs):
        recipe = Mock()
        recipe.metrics = {MetricSettingTest.METRIC_KEY : MetricSettingTest.METRIC_VALUE}
        return recipe

    def testAddRecipe(self):
        recipe_name = 'recipe_name'
        recipe_url = 'recipe_url'
        mkey = MetricSettingTest.METRIC_KEY
        mval = MetricSettingTest.METRIC_VALUE
        
        self.setting.add_recipe(recipe_name)
        self.failUnless(mkey in self.setting.metrics)
        self.failUnless(self.setting.metrics[mkey] == mval)

        self.setting.metrics = {}
        recipe = Mock()
        recipe.metrics = {mkey:mval}
        self.setting.add_recipe(recipe)
        self.failUnless(mkey in self.setting.metrics)
        self.failUnless(self.setting.metrics[mkey] == mval)


    testAddRecipe = patch('fiveruns.dash.recipes.find', mock_find)(testAddRecipe)
