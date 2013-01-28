"""Main entry point
"""
import datetime

from pyramid.config import Configurator
from pyramid.events import NewRequest
from pyramid.renderers import JSON

from pyelasticsearch import ElasticSearch


def attach_elasticsearch(event):
    request = event.request
    event.request.es = request.registry.es


def main(global_config, **settings):
    config = Configurator(settings=settings)
    config.include("cornice")
    config.scan("monolith.views")
    config.add_static_view(name='media', path='monolith:media')
    json_renderer = JSON()

    def datetime_adapter(obj, request):
        return obj.isoformat()

    def date_adapter(obj, request):
        return '%sT00:00:00' % obj.isoformat()

    json_renderer.add_adapter(datetime.datetime, datetime_adapter)
    json_renderer.add_adapter(datetime.date, date_adapter)
    config.add_renderer('json', json_renderer)
    settings = config.registry.settings

    host = settings.get('elasticsearch.host', 'http://localhost:9200')
    config.registry.es = ElasticSearch(host)
    config.add_subscriber(attach_elasticsearch, NewRequest)
    return config.make_wsgi_app()
