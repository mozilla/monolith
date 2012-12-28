from tastypie.resources import Resource


class ESResource(Resource):

    class Meta:
        resource_name = 'query'
