import json

import mock
from unittest2 import TestCase
from webtest import TestApp

from monolith.web import main


class TestViews(TestCase):

    def setUp(self):
        global_config = {}
        wsgiapp = main(global_config)
        self.app = TestApp(wsgiapp)

    def test_get_info(self):
        res = self.app.get('/')
        info = res.json
        self.assertEqual(set(info['fields']),
                         set(['downloads_count', 'pageviews', 'users_count']))

    def test_query_time(self):
        mock_search = mock.Mock()
        mock_search.return_value = {
            'hits': {
                'hits': [{
                    '_id': 'mjI8-cQOQ3iz9bFP15wQLg',
                    '_index': 'time_2012-01',
                    '_source': {
                        'add_on': 1,
                        'app_uuid': '1d3789e2f4ab4d659ca67b01f0bee534',
                        'date': '2012-01-01T00:00:00',
                        'downloads_count': 1060,
                        'os': 'Ubuntu',
                        'users_count': 13041,
                    },
                    '_type': 'downloads',
                }],
            },
            'timed_out': False,
            'took': 106,
        }

        start = '2012-01-01T00:00:00'
        end = '2012-01-03T00:00:00'
        with mock.patch('pyelasticsearch.client.ElasticSearch.search',
                        mock_search):
            res = self.app.post('/v1/time', json.dumps({
                'query': {'match_all': {}},
                'filter': {'range': {'date': {'gte': start, 'lte': end}}},
            }))
        self.assertEqual(res.status_code, 200)
        self.assertTrue('hits' in res.json)

    def test_query_time_error(self):
        mock_search = mock.Mock()

        def fail(*args, **kw):
            from pyelasticsearch import ElasticHttpError
            raise ElasticHttpError(500, 'SearchPhaseExecutionException...')

        mock_search.side_effect = fail
        with mock.patch('pyelasticsearch.client.ElasticSearch.search',
                        mock_search):
            res = self.app.post('/v1/time', json.dumps({
                'query': ['invalid query'],
            }), expect_errors=True)
        self.assertEqual(res.status_code, 500)
        self.assertTrue('SearchPhaseExecutionException' in res.body, res.body)

    def test_query_time_invalid_json(self):
        res = self.app.post('/v1/time', '{"que"""', expect_errors=True)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.json['status'], 'error')
