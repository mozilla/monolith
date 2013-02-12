from collections import defaultdict
import datetime
import random
import sys

from pyelasticsearch import ElasticSearch


def feed(index='monolith', type='downloads', es_port=9200):
    client = ElasticSearch('http://0.0.0.0:%d/' % es_port)
    platforms = ['Mac OS X', 'Windows 8', 'Ubuntu']

    # indexing a year of data (2012)
    first_day = datetime.datetime(2012, 1, 1)
    last_day = datetime.datetime(2012, 12, 31)
    day_range = last_day - first_day

    for month in range(1, 13):
        name = 'time_2012-%.2d' % month
        try:
            client.delete_index(name)
        except Exception:
            pass
        client.create_index(name, settings={
            'number_of_shards': 1,
            'number_of_replicas': 0,
            'analysis': {'analyzer': {'default': {
                'type': 'custom', 'tokenizer': 'keyword'
            }}},
            'store': {'compress': {'stored': 'true'}},
        })

    # indexing 100 apps
    for add_on in range(100):
        docs = defaultdict(list)
        for delta in range(day_range.days):
            date = first_day + datetime.timedelta(days=delta)
            data = {'date': date,
                    'os': random.choice(platforms),
                    'downloads_count': random.randint(1000, 1500),
                    'users_count': random.randint(10000, 15000),
                    'add_on': add_on + 1}
            docs[date.month].append(data)
        for month, values in docs.items():
            client.bulk_index('time_2012-%.2d' % month, type, values)
            sys.stdout.write('.')
            sys.stdout.flush()

    client.optimize('time_*', max_num_segments=1, wait_for_merge=True)
    client.flush()
    sys.stdout.write('\nDone!\n')


if __name__ == '__main__':
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
    else:
        port = 9200

    feed(es_port=port)

