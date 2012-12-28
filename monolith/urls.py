from django.conf.urls.defaults import include, patterns, url

from tastypie.api import Api

from metrics.resources import ESResource, IndexResource, MetricResource

api = Api(api_name='es')
api.register(ESResource())
api.register(IndexResource())
api.register(MetricResource())

urlpatterns = patterns('',
    url(r'^', include(api.urls)),
    url(r'^$', 'monolith.views.home', name='home'),
)

handler500 = handler404 = handler403 = 'monolith.views.error'
