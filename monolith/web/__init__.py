"""Main entry point
"""
import datetime
import logging

from pyramid.config import Configurator
from pyramid.events import NewRequest
from pyramid.renderers import JSON

from pyelasticsearch import ElasticSearch
from statsd import StatsClient


logger = logging.getLogger('monolith.web')


def attach_request(event):
    request = event.request
    event.request.es = request.registry.es
    event.request.prefix = request.registry.prefix
    event.request.statsd = request.registry.statsd


def main(global_config, **settings):
    config = Configurator(settings=settings)
    config.include('cornice')
    config.scan('monolith.web.views')
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
    prefix = settings.get('elasticsearch.prefix', '')

    logger.info('Config is set to query %s/%stime_*' % (host, prefix))

    statsd_settings = {
        'host': settings.get('statsd.host', 'localhost'),
        'port': int(settings.get('statsd.port', 8125)),
        'prefix': settings.get('statsd.prefix', ''),
    }
    config.registry.statsd = StatsClient(**statsd_settings)

    # XXX we need a way to lazy-inject this to the cornice views
    cors_origins = settings.get('cors.origins', '*')
    cors_origins = cors_origins.split(',')

    config.registry.es = ElasticSearch(host)
    config.registry.prefix = prefix
    config.add_subscriber(attach_request, NewRequest)

    return config.make_wsgi_app()
