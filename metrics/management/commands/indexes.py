from optparse import make_option

from django.core.management.base import BaseCommand

from elasticutils import get_es

class Command(BaseCommand):

    option_list = BaseCommand.option_list + (
        make_option('--delete', action='store_true', default=False,
                    dest='delete', help='Delete the index.'),
    )

    def handle(self, *args, **options):
        conn = get_es()
        if options.get('delete'):
            conn.delete_index('monolith')
        conn.create_index('monolith')
        mapping = {
            'name': {
                'store': 'yes',
                'type': 'string',
            },
            'date': {
                'store': 'yes',
                'type': 'date',
                'format': 'yyyy-MM-dd',
            },
            'key': {
                'store': 'yes',
                'type': 'string',
            },
            'value': {
                'store': 'yes',
                'type': 'integer',
            }
        }
        conn.put_mapping('metrics',
                         {'properties': mapping},
                         ['monolith'])
