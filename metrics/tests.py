import json

from urllib import unquote
from urlparse import urlparse

from django import test
from django.test.client import FakePayload

from metrics.models import Metric

import mock
from nose.tools import eq_

from tastypie_test import ResourceTestCase, TestApiClient


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
        eq_(len(Metric.objects.filter(name='addons.downloads.count')), 1)

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
class TestESResource(ResourceTestCase):
    url = '/es/search/'

    def setUp(self):
        super(TestESResource, self).setUp()
        self.api_client = MetricsApiClient()

    def test_get_no_json(self, search):
        res = self.api_client.get(self.url, format='json')
        eq_(res.status_code, 200)
        eq_(len(json.loads(res.content)['objects']), 0)

    def test_get_bad_json(self, search):
        res = self.api_client.get(self.url, format='json', data=None)
        eq_(res.status_code, 400)

    def test_get_filter(self, search):
        data = {'filter': {'term': {'name': 'addons.downloads.count.total'}}}
        search.return_value = {u'hits': {u'hits': [
            {u'_score': 1.0, u'_source':
                {u'date': u'2012-12-27', u'key': u'',
                 u'name': u'some.name', u'value': 2681}, u'_index':
             u'monolith'}]}}
        res = self.api_client.get(self.url, format='json', data=data)
        eq_(res.status_code, 200)
        data = json.loads(res.content)
        eq_(len(data['objects']), 1)
        result = data['objects'][0]
        eq_(result['date'], '2012-12-27')
        eq_(result['value'], 2681)

    def test_get_fields(self, search):
        data = {'filter': {'term': {'name': 'addons.downloads.count.total'}},
                'fields': ['value']}
        search.return_value = {u'hits': {u'hits': [
            {u'_score': 1.0,
             'fields': {u'date': None, u'value': 2681}}]}}
        res = self.api_client.get(self.url, format='json', data=data)
        eq_(res.status_code, 200)
        data = json.loads(res.content)
        eq_(len(data['objects']), 1)
        result = data['objects'][0]
        eq_(result['date'], None)
        eq_(result['value'], 2681)
