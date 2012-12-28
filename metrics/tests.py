from django import test
from metrics.models import Metric

from nose.tools import eq_


class TestMetrics(test.TestCase):
    fixtures = ['metrics.json']

    def test_metrics(self):
        eq_(len(Metric.objects.filter(name='addons.downloads.count')), 1)
