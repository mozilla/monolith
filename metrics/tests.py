import json

from urllib import unquote
from urlparse import urlparse

from django import test
from django.test.client import FakePayload

from metrics.models import Metric

import mock
from nose.tools import eq_

from tastypie_test import ResourceTestCase, TestApiClient

adc = 'addons.downloads.count'
adca = 'addons.downloads.count.addon'


class MetricsApiClient(TestApiClient):
    """A test client that allows JSON in the body for GETs."""

    def get(self, uri, format='json', data='',
            authentication=None, **kwargs):
        parsed = urlparse(uri)
        content_type = self.get_content_type(format)
        kwargs['content_type'] = content_type

        req = {
            'CONTENT_LENGTH': 0,
            'CONTENT_TYPE': 'application/json',
            'PATH_INFO': unquote(parsed[2]),
            'REQUEST_METHOD': 'GET',
        }

        if data is not None:
            data = self.serializer.serialize(data, format=content_type)
            req.update({
                'CONTENT_LENGTH': len(data),
                'wsgi.input': FakePayload(data)
            })

        response = self.client.request(**req)
        return response


class TestMetrics(test.TestCase):
    fixtures = ['metrics.json']

    def test_metrics(self):
        eq_(len(Metric.objects.filter(name='addons.downloads.count')), 2)

    @mock.patch('pyes.es.ES.index')
    def test_index(self, index):
        Metric.objects.get(pk=1).index()
        assert index.called

    @mock.patch('pyes.es.ES.delete')
    def test_unindex(self, delete):
        Metric.objects.get(pk=1).unindex()
        assert delete.called


class TestIndexResource(ResourceTestCase):
    fixtures = ['metrics.json']
    url = '/es/index/1/'

    @mock.patch('pyes.es.ES.index')
    def test_patch(self, index):
        self.api_client.patch(self.url, data={})
        assert index.called
        assert Metric.objects.filter(pk=1).exists()

    @mock.patch('pyes.es.ES.delete')
    def test_delete(self, delete):
        self.api_client.delete(self.url)
        assert delete.called
        assert Metric.objects.filter(pk=1).exists()


@mock.patch('pyes.es.ES.search')
class TestRawResource(ResourceTestCase):
    url = '/es/raw/'

    def setUp(self):
        super(TestRawResource, self).setUp()
        self.api_client = MetricsApiClient()

    def test_get_no_json(self, search):
        res = self.api_client.get(self.url)
        eq_(res.status_code, 400)

    def test_get_bad_json(self, search):
        res = self.api_client.get(self.url, data=None)
        eq_(res.status_code, 400)

    def test_get_filter(self, search):
        data = {'filter': {'term': {'name': 'addons.downloads.count.total'}}}
        search.return_value = {u'hits': {u'hits': [
            {u'_score': 1.0, u'_source':
                {u'date': u'2012-12-27', u'key': u'',
                 u'name': u'some.name', u'value': 2681}, u'_index':
             u'monolith'}]}}
        res = self.api_client.get(self.url, data=data)
        eq_(res.status_code, 200)
        data = json.loads(res.content)
        eq_(len(data['hits']), 1)
        result = data['hits']['hits'][0]['_source']
        eq_(result['date'], '2012-12-27')
        eq_(result['value'], 2681)


@mock.patch('pyes.es.ES.search')
class TestMonolith(ResourceTestCase):
    fixtures = ['metrics.json']
    url = '/es/search/'

    def setUp(self):
        super(TestMonolith, self).setUp()
        self.api_client = MetricsApiClient()

    def test_added(self, search):
        data = {'names': [adc], 'start': '2009-07-13', 'end': '2010-07-13'}
        res = self.api_client.get(self.url, data=data)
        eq_(res.status_code, 200)
        called = search.call_args[0][0]
        eq_(called['sort'], {'date': {'order': 'asc'}})
        eq_(called['fields'], ['date', 'value', 'name'])

    def test_multiple(self, search):
        search.return_value = {'hits': {'hits': [
            {'fields': {'date': '2009-07-13', 'value': 1681, 'name': adc}},
            {'fields': {'date': '2009-07-13', 'value': 1681, 'name': adca}},
            {'fields': {'date': '2009-07-15', 'value': 2683, 'name': adc}},
        ]}}
        data = {'names': [adc, adca],
                'start': '2009-07-13',
                'end': '2009-07-16'}
        res = self.api_client.get(self.url, data=data)
        eq_(res.status_code, 200)
        content = json.loads(res.content)
        eq_(len(content[adc]), 3)
        eq_(len(content[adca]), 3)
        eq_(content[adc][0]['date'], '2009-07-13')

    def test_filled(self, search):
        search.return_value = {'hits': {'hits': [
            {'fields': {'date': '2009-07-13', 'value': 1681, 'name': adc}},
            {'fields': {'date': '2009-07-15', 'value': 2683, 'name': adca}},
        ]}}
        data = {'start': '2009-07-13', 'end': '2009-07-16', 'names': [adc]}
        res = self.api_client.get(self.url, data=data)
        eq_(res.status_code, 200)
        content = json.loads(res.content)
        eq_(content[adc][0]['value'], 1681)
        eq_(content[adc][1]['value'], 0)

    def test_missing(self, search):
        res = self.api_client.get(self.url, data={})
        eq_(res.status_code, 400)
        content = json.loads(res.content)
        eq_(set(['start', 'end', 'names']), set(content.keys()))
