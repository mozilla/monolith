import simplejson as json

from cornice import Service
from colander import MappingSchema, SchemaNode, Date, Seq

from pyelasticsearch.exceptions import ElasticHttpError


class ElasticSearchQuery(MappingSchema):
    start = SchemaNode(Date(), location='body', type='datetime.datetime')
    end = SchemaNode(Date(), location='body', type='datetime.datetime')
    names = SchemaNode(Seq(), location='body')


info = Service(name='info', path='/',
               cors_policy={'origins': ('*',), 'credentials': True})


@info.get(renderer='json')
def get_info(request):
    """Returns info on the Monolith server, like the list of queriable fields
    """
    # XXX config ?
    return {'fields': ['downloads_count', 'users_count', 'pageviews'],
            'es_endpoint': '/v1/time'}


es_time = Service(
    name='elasticsearch-time',
    path='/v1/time',
    description="Raw access to ES time-series data.",
    cors_policy={'origins': ('*',), 'credentials': True})


es_totals = Service(
    name='elasticsearch-totals',
    path='/v1/totals/{doc_type}/{_id}',
    description="Raw access to ES lifetime total data.")


def valid_json_body(request):
    # XXX put this back in cornice.validators
    try:
        request.validated['body'] = request.json
    except json.JSONDecodeError as exc:
        request.errors.add('body', description=str(exc))


@es_time.post(validators=(valid_json_body,), renderer='json')
def query_es_time(request):
    try:
        return request.es.search(request.validated['body'], index='time_*')
    except ElasticHttpError as e:
        request.response.status = e.status_code
        return e.error


@es_totals.get(renderer='json')
def get_es_totals(request):
    match = request.matchdict
    try:
        return request.es.get('totals', match['doc_type'], match['_id'])
    except ElasticHttpError as e:
        request.response.status = e.status_code
        return e.error
