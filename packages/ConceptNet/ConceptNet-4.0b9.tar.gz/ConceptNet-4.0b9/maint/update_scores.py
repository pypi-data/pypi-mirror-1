from csc.util import queryset_foreach
from conceptnet4.models import Sentence, Assertion, RawAssertion

queryset_foreach(Assertion.objects.exclude(language__id='en'), lambda x: x.update_score(),
batch_size=100)
queryset_foreach(RawAssertion.objects.exclude(language__id='en'), lambda x: x.update_score(),
batch_size=100)
queryset_foreach(Sentence.objects.exclude(language__id='en'), lambda x: x.update_score(),
batch_size=100)

