import uuid

from django.db import models
from elasticutils import get_es


class Metric(models.Model):
    date = models.DateField(db_index=True)
    key = models.CharField(max_length=255, db_index=True)
    # Let's use the graphite standard, all names are lower case,
    # delimited by . and in order of specificity.
    name = models.CharField(max_length=255, db_index=True)
    value = models.IntegerField(db_index=True)

    # A uuid field so you can spot if this metric has been imported already
    # into monolith. If not supplied, we'll make one up for you.
    uuid = models.CharField(max_length=255, db_index=True, unique=True)

    class Meta:
        db_table = 'metric'

    def index(self):
        conn = get_es()
        data = {
            'date': self.date.strftime('%Y-%m-%d'),
            'key': self.key,
            'name': self.name,
            'value': self.value
        }
        conn.index(data, 'monolith', 'metrics/%s/' % self.pk)

    def save(self, *args, **kw):
        if not self.uuid:
            self.uuid = str(uuid.uuid4())
        super(Metric, self).save(*args, **kw)

    def unindex(self):
        conn = get_es()
        conn.delete('monolith', 'metrics', self.pk)
