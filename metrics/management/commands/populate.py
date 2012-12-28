from datetime import datetime, timedelta
from optparse import make_option
from random import randint

from django.core.management.base import BaseCommand

from metrics.models import Metric


class Command(BaseCommand):

    option_list = BaseCommand.option_list + (
        make_option('--k', action='store', default='', dest='key'),
        make_option('--n', action='store', default='some.name', dest='name'),
    )

    def handle(self, *args, **options):
        today = datetime.today()
        for x in range(0, 1000):
            data = {
                'value': randint(0, 5000),
                'key': options.get('key'),
                'name': options.get('name'),
                'date': today - timedelta(days=x)
            }
            obj = Metric.objects.create(**data)
            obj.index()
