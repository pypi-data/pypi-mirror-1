from csamoa.conceptnet.models import Frame, Batch, RawPredicate

from django.db import models
from django.contrib.auth.models import User
from csamoa.corpus.models import Sentence, Language


class TaggedSentence(models.Model):
    id = models.IntegerField(primary_key=True)
    text = models.TextField(blank=False)
    language = models.ForeignKey(Language)

    class Meta:
        db_table = 'tagged_sentences'
### FINISH ME #######################################################
