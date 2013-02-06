import unittest

from webtest import TestApp
from monolith import main


class TestViews(unittest.TestCase):

    def setUp(self):
        global_config = {}
        wsgiapp = main(global_config)
        self.app = TestApp(wsgiapp)

    def test_get_info(self):
        res = self.app.get('/')
        info = res.json
        self.assertEqual(info['fields'],
                         ['downloads_count', 'users_count'])
