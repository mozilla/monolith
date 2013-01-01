from collections import defaultdict
from datetime import timedelta
import json

from django.core.exceptions import ObjectDoesNotExist
from django import http
from django import forms

from elasticutils import get_es
from tastypie import fields
from tastypie.authorization import Authorization
from tastypie.exceptions import ImmediateHttpResponse, NotFound
from tastypie.resources import Resource, ModelResource

from curling.lib import Encoder

from models import Metric


class RawResource(Resource):
    """Raw access to ES."""

    class Meta:
        resource_name = 'raw'
        list_allowed_methods = ['get']
        always_return_data = True

    def pre_json(self, request):
        return json.loads(request.body)

    def obj_get_list(self, request, **kwargs):
        es = get_es()

        try:
            query = json.loads(request.body)
        except ValueError:
            raise ImmediateHttpResponse(response=http.HttpResponseBadRequest())

        if not query:
            raise ImmediateHttpResponse(response=http.HttpResponseBadRequest())

        # TODO: This is just a straight pass through, wonder if we should be
        # doing more here.
        response = http.HttpResponse(json.dumps(es.search(query, 'monolith')),
                                     content_type='application/json')
        raise ImmediateHttpResponse(response=response)


class MarketplaceForm(forms.Form):
    start = forms.DateField()
    end = forms.DateField()
    names = forms.MultipleChoiceField()

    def __init__(self, *args, **kw):
        super(MarketplaceForm, self).__init__(*args, **kw)
        self.fields['names'].choices = [(v, v) for v in
            Metric.objects.values_list('name', flat=True).distinct()]

    def clean(self):
        data = self.cleaned_data
        if not ('start' in data or 'end' in data):
            return

        start, end = data['start'], data['end']
        if start > end:
            raise forms.ValidationError('Start greater than end.')
        self._diff = (end - start).days
        if self._diff > 365:
            raise forms.ValidationError('Cannot request more than 365 days.')
        return data

    @property
    def formatted_data(self):
        names = [{'term': {'name': name}} for name in self.cleaned_data['names']]
        return {
            'sort': {'date': {'order': 'asc'}},
            'fields': ['date', 'value', 'name'],
            'filter':
                {'and': [
                    {'or': names},
                    {'range': {'date': {'gte': self.cleaned_data['start'],
                                        'lt': self.cleaned_data['end']}}},
                ]}
            }


class MarketplaceResource(Resource):
    """
    Similar to RawResource, but forms the queries for you, because there
    are some things ES can't do.

    Adds fields to the incoming request:
        size: 365 (if not specified)
        fields: date, value (if not specified)
        sort: date asc (if not specified)

    On the response it parses the data a little bit more:
        fills in any missing dates with zeros (if dates specified)

    The result is a dictionary of lists of the results, keyed on the names.
    """

    class Meta:
        resource_name = 'search'
        list_allowed_methods = ['get']

    def obj_get_list(self, request, **kwargs):
        es = get_es()
        form = MarketplaceForm(json.loads(request.body))
        if not form.is_valid():
            res = http.HttpResponseBadRequest(content=json.dumps(form.errors),
                                              content_type='application/json')
            raise ImmediateHttpResponse(response=res)

        key = lambda *args: '-'.join(args)
        result = es.search(form.formatted_data, 'monolith')
        objects = dict([key(v['fields']['name'],
                            v['fields']['date']), v['fields']]
                        for v in result['hits']['hits'])
        result = defaultdict(list)
        for name in form.cleaned_data['names']:
            for x in range(0, form._diff):
                day = (form.cleaned_data['start'] +
                       timedelta(days=x)).strftime('%Y-%m-%d')
                entry = objects.get(key(name, day), {})
                result[name].append({'date': entry.get('date', day),
                                     'value': entry.get('value', 0)})

        response = http.HttpResponse(json.dumps(result),
                                     content_type='application/json')
        raise ImmediateHttpResponse(response=response)

        return result

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
