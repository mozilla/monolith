"""Main entry point
"""
import datetime
import logging

from pyramid.config import Configurator
from pyramid.events import NewRequest
from pyramid.renderers import JSON

from pyelasticsearch import ElasticSearch
import statsd


logger = logging.getLogger('monolith.web')


def attach_elasticsearch(event):
    request = event.request
    event.request.es = request.registry.es


def main(global_config, **settings):
    config = Configurator(settings=settings)
    config.include("cornice")
    config.scan("monolith.web.views")
    config.add_static_view(name='media', path='monolith.web:media')
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

    # statsd settings
    statsd_settings = {'STATSD_HOST': settings.get('statsd.host', 'localhost'),
                       'STATSD_PORT': int(settings.get('statsd.port', 8125)),
                       'STATSD_SAMPLE_RATE': float(settings.get('statsd.sample',
                                                   1.0)),
                       'STATSD_BUCKET_PREFIX': settings.get('statsd.prefix',
                                                            '')}

    statsd.init_statsd(statsd_settings)

    # XXX we need a way to lazy-inject this to the cornice views
    cors_origins = settings.get('cors.origins', '*')
    cors_origins = cors_origins.split(',')

    config.registry.es = ElasticSearch(host)
    config.add_subscriber(attach_elasticsearch, NewRequest)
    return config.make_wsgi_app()
