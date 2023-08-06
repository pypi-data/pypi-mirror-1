from django.db import models


class BigManager(models.Manager):
    def get_query_set(self):
        return super(BigManager, self).get_query_set().filter(value__gte=100)

class KeyValue(models.Model):
    key = models.CharField(max_length=50)
    value = models.IntegerField(default=0)

    objects = models.Manager()
    big = BigManager()

    def __unicode__(self):
        return '%s=%d' % (self.key, self.value)
    def __repr__(self):
        return '%s=%d' % (self.key, self.value)


from django_templatequery.tests.test_query_tags import *
