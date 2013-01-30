import simplejson as json

from cornice import Service
from colander import MappingSchema, SchemaNode, Date, Seq

from pyelasticsearch.exceptions import ElasticHttpError


class ElasticSearchQuery(MappingSchema):
    start = SchemaNode(Date(), location='body', type='datetime.datetime')
    end = SchemaNode(Date(), location='body', type='datetime.datetime')
    names = SchemaNode(Seq(), location='body')


info = Service(name='info', path='/')


@info.get(renderer='json')
def get_info(request):
    """Returns info on the Monolith server, like the list of queriable fields
    """
    return {'fields': ['downloads_count', 'users_count'],
            'es_endpoint': '/es'}


es = Service(
    name='elasticsearch',
    path='/es',
    description="Raw access to ES")


def valid_json_body(request):
    # XXX put this back in cornice.validators
    try:
        request.validated['body'] = request.json
    except json.JSONDecodeError, exc:
        request.errors.add('body', description=str(exc))


@es.post(validators=(valid_json_body,), renderer='json')
def query_es(request):
    try:
        return request.es.search(request.validated['body'], index='monolith')
    except ElasticHttpError as e:
        request.response.status = e.status_code
        return e.error
