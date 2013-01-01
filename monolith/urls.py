from django.conf.urls.defaults import include, patterns, url

from tastypie.api import Api

from metrics.resources import (IndexResource, MarketplaceResource,
                               MetricResource, RawResource)

api = Api(api_name='es')
api.register(MetricResource())
api.register(MarketplaceResource())
api.register(IndexResource())
api.register(RawResource())

urlpatterns = patterns('',
    url(r'^', include(api.urls)),
    url(r'^$', 'monolith.views.home', name='home'),
)

handler500 = handler404 = handler403 = 'monolith.views.error'
