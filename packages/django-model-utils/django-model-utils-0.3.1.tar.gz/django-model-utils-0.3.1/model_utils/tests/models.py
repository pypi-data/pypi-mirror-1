from django.db import models

from model_utils.models import InheritanceCastModel, TimeStampedModel
from model_utils.managers import QueryManager


class InheritParent(InheritanceCastModel):
    pass

class InheritChild(InheritParent):
    pass

class TimeStamp(TimeStampedModel):
    pass

class Post(models.Model):
    published = models.BooleanField()
    confirmed = models.BooleanField()
    order = models.IntegerField()

    objects = models.Manager()
    public = QueryManager(published=True)
    public_confirmed = QueryManager(models.Q(published=True) &
                                    models.Q(confirmed=True))
    public_reversed = QueryManager(published=True).order_by('-order')

    class Meta:
        ordering = ('order',)
