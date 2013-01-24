"""Main entry point
"""
from pyramid.config import Configurator
from pyramid.events import NewRequest

from elasticutils import get_es


def attach_elasticsearch(event):
    request = event.request
    event.request.es = request.registry.es


def main(global_config, **settings):
    config = Configurator(settings=settings)
    config.include("cornice")
    config.scan("monolith.views")

    settings = config.registry.settings

    hosts = settings.get('elasticsearch.hosts', 'localhost:9200')
    hosts = hosts.split(',')
    config.registry.es = get_es(hosts=hosts)

    config.add_subscriber(attach_elasticsearch, NewRequest)
    return config.make_wsgi_app()
