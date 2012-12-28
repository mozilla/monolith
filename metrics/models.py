from django.db import models
from elasticutils import get_es


class Metric(models.Model):
    date = models.DateField(db_index=True)
    key = models.CharField(max_length=255, db_index=True)
    name = models.CharField(max_length=255, db_index=True)
    value = models.IntegerField(db_index=True)

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

    def unindex(self):
        conn = get_es()
        conn.delete('monolith', 'metrics', self.pk)
