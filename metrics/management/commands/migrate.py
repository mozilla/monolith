from optparse import make_option

from django.core.management.base import BaseCommand
from django.db import utils

from metrics.models import Metric

import json


def fix_name(name):
    # This will do for now, but we should probably do some work here fixing
    # up the names.
    name.replace('_', '.')
    return name.lower()


class Command(BaseCommand):

    option_list = BaseCommand.option_list + (
        make_option('--zamboni', action='store', dest='zamboni',
                    help='Path to the JSON file containing zamboni DB access '
                         'to the database. This can be a copy of '
                         'dictionary from settings.'),
        # For example:
        # {"ENGINE": "django.db.backends.mysql", "NAME": "zamboni", ...}
        make_option('--raise', action='store_true', dest='raise',
                    help='Re-raise errors when the occur, rather than skip.')
    )

    def handle(self, *args, **options):
        zamboni = options['zamboni']
        if not zamboni:
            print 'No path to zamboni given.'
            return

        db_settings = json.load(open(zamboni, 'r'))
        backend = utils.load_backend(db_settings['ENGINE'])
        wrapper = backend.DatabaseWrapper(db_settings)
        cursor = wrapper.cursor()
        start = 0
        limit = 1000  # The number of records to do at a time.
        count = {'imported': 0, 'skipped': 0, 'errors': 0}
        sql = 'SELECT * FROM global_stats ORDER BY id LIMIT %s,%s'
        cursor.execute(sql, (start, limit))
        results = cursor.fetchall()
        while results:
            for row in results:
                uuid = 'global_stats:%s' % row[0]
                if not Metric.objects.filter(uuid=uuid).exists():
                    try:
                        obj = Metric.objects.create(uuid=uuid, date=row[3],
                                                    name=fix_name(row[1]),
                                                    value=row[2])
                        count['imported'] += 1
                        obj.index()
                    except:
                        count['errors'] += 1
                        if options['raise']:
                            raise

                else:
                    count['skipped'] += 1

            # Bump our start and re-fetch.
            start += limit
            cursor.execute(sql, (start, limit))
            results = cursor.fetchall()

        print 'Import completed.'
        print 'Processed:', sum(count.values())
        for k, v in count.items():
            print '%s:' % k.title(), v
