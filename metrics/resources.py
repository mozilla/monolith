import json

from django.core.exceptions import ObjectDoesNotExist
from django import http

from elasticutils import get_es
from tastypie import fields
from tastypie.authorization import Authorization
from tastypie.exceptions import ImmediateHttpResponse, NotFound
from tastypie.resources import Resource, ModelResource

from models import Metric


class Hit(object):
    def __init__(self, **data):
        for k, v in data.items():
            setattr(self, k, v)


class ESResource(Resource):
    date = fields.DateField(readonly=True, attribute='date', default=None)
    key = fields.CharField(readonly=True, attribute='key', default=None)
    name = fields.CharField(readonly=True, attribute='name', default=None)
    value = fields.IntegerField(readonly=True, attribute='value', default=None)

    class Meta:
        resource_name = 'search'
        list_allowed_methods = ['get']
        always_return_data = True
        max_limit = 365
        limit = 365

    def obj_get_list(self, request, **kwargs):
        es = get_es()
        try:
            query = json.loads(request.body)
        except ValueError:
            raise ImmediateHttpResponse(response=http.HttpResponseBadRequest())
        result = es.search(query, 'monolith')
        return [Hit(**data.get('_source', data.get('fields', {})))
                for data in result['hits']['hits']]


class MetricResource(ModelResource):

    class Meta:
        queryset = Metric.objects.filter()
        resource_name = 'metric'
        authorization = Authorization()


class IndexResource(ModelResource):

    class Meta:
        queryset = Metric.objects.filter()
        resource_name = 'index'
        allowed_methods = ['patch', 'delete']
        authorization = Authorization()

    def obj_update(self, bundle, request, **kwargs):
        # Skip the whole object manipulation thing.
        bundle.obj.index()
        return bundle

    def obj_delete(self, request=None, **kwargs):
        # Ditto, don't delete.
        try:
            obj = self.obj_get(request, **kwargs)
        except ObjectDoesNotExist:
            raise NotFound

        obj.unindex()
