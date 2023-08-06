from csc.util import queryset_foreach
from conceptnet4.models import Sentence, Assertion, RawAssertion

queryset_foreach(Assertion.objects.all(), lambda a: a.update_raw_cache(),
batch_size=100)

