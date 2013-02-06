import mock
from unittest2 import TestCase
from webtest import TestApp

from monolith import main


class TestViews(TestCase):

    def setUp(self):
        global_config = {}
        wsgiapp = main(global_config)
        self.app = TestApp(wsgiapp)

    def test_get_info(self):
        res = self.app.get('/')
        info = res.json
        self.assertEqual(info['fields'],
                         ['downloads_count', 'users_count'])

    def test_get_totals(self):
        mock_get = mock.Mock()
        mock_get.return_value = {
            '_type': 'apps', 'exists': True, '_index': 'totals',
            '_source': {'downloads': 1, 'users': 2},
            '_version': 1, '_id': '1',
        }
        with mock.patch('pyelasticsearch.client.ElasticSearch.get', mock_get):
            res = self.app.get('/v1/totals/apps/1')
        self.assertTrue('_source' in res.json)
        self.assertEqual(res.json['_source'], {'downloads': 1, 'users': 2})

    def test_get_totals_not_found(self):
        mock_get = mock.Mock()
        data = {
            '_type': 'apps', '_id': '2', 'exists': False, '_index': 'totals',
        }

        def fail(*args):
            from pyelasticsearch import ElasticHttpNotFoundError
            raise ElasticHttpNotFoundError(404, data)

        mock_get.side_effect = fail
        with mock.patch('pyelasticsearch.client.ElasticSearch.get', mock_get):
            res = self.app.get('/v1/totals/apps/2', expect_errors=True)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(res.json, data)
