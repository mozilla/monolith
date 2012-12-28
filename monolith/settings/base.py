# This is your project's main settings file that can be committed to your
# repo. If you need to override a setting locally, use settings_local.py

from funfactory.settings_base import *

# Name of the top-level module where you put all your apps.
# If you did not install Playdoh with the funfactory installer script
# you may need to edit this value. See the docs about installing from a
# clone.
PROJECT_MODULE = 'monolith'

# Defines the views served for root URLs.
ROOT_URLCONF = '%s.urls' % PROJECT_MODULE

INSTALLED_APPS = [
    'funfactory',
    'django_nose',
    'django_statsd',
    'monolith',
    # Now our custom stuff.
    'metrics',
]

USE_I18N = False
USE_L10N = False

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)
JINJA_CONFIG = lambda: ''

SITE_URL = 'http://127.0.0.1:8000'
LOGIN_URL = '/'

# Should robots.txt deny everything or disallow a calculated list of URLs we
# don't want to be crawled?  Default is false, disallow everything.
# Also see http://www.google.com/support/webmasters/bin/answer.py?answer=93710
ENGAGE_ROBOTS = False

MIDDLEWARE_CLASSES = (
    'django_statsd.middleware.GraphiteMiddleware',
)

LOGGING = dict(loggers=dict(playdoh = {'level': logging.DEBUG}))

ES_DUMP_CURL = '/tmp/curl_dump.log'
ES_HOSTS = ['127.0.0.1:9200']
ES_INDEXES = {
    'default': 'monolith'
}
