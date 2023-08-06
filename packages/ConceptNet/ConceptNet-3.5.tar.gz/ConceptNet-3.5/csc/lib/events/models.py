from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from django.db import models
from datetime import datetime

class Activity(models.Model):
    name = models.TextField()
    def __str__(self):
        return self.name
    class Meta:
        verbose_name_plural = 'Activities'

class Event(models.Model):
    """
    Indicates that an object was created or possibly modified by an Activity.
    """
    user         = models.ForeignKey(User)
    content_type = models.ForeignKey(ContentType)
    object_id    = models.PositiveIntegerField()
    object       = generic.GenericForeignKey('content_type', 'object_id')
    activity     = models.ForeignKey(Activity)
    timestamp    = models.DateTimeField(default=datetime.now)

    @classmethod
    def record_event(cls, obj, user, activity):
        ctype = ContentType.objects.get_for_model(obj)
        event = cls.objects.create(user=user, content_type=ctype,
                           object_id=obj._get_pk_val(),
                           activity=activity)
        return event

