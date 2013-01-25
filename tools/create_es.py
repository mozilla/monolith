from pyelasticsearch import ElasticSearch
import sys
import random
import datetime


def feed(index='monolith', type='downloads'):
    client = ElasticSearch('http://localhost:9200/')
    platforms = ['Mac OS X', 'Windows 8', 'Ubuntu']

    # indexing a year of data (2012)
    first_day = datetime.datetime(2012, 1, 1)
    last_day = datetime.datetime(2012, 12, 31)
    day_range = last_day - first_day

    for delta in range(day_range.days):
        data = {'date': first_day + datetime.timedelta(days=delta),
                'os': random.choice(platforms),
                'count': random.randint(0, 1000),
                'add_on': 1}

        client.index(index, type, data)
        sys.stdout.write('.')
        sys.stdout.flush()

    sys.stdout.write('\nDone!\n')


if __name__ == '__main__':
    feed()

