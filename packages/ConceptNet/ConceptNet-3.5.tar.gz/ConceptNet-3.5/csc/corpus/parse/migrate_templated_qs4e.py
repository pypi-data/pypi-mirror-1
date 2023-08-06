#!/usr/bin/env python
from conceptnet4.models import Assertion, Batch, RawAssertion, Frame,\
  Frequency, Relation, SurfaceForm, Concept, Rating
import conceptnet.models as cn3
from corpus.models import Sentence, Language, Activity
from django.contrib.auth.models import User
from corpus.parse.adverbs import map_adverb
from itertools import islice
import yaml
from csamoa.util import queryset_foreach
from django.db import Q

csamoa4_activity = Activity.objects.get(name='csamoa4 self-rating')
good_acts = [ 16, 20, 22, 24, 28, 31, 32 ]
en = Language.get('en')

def process_predicate(pred, batch):
    frametext = pred.frame.text
    matches = {1: pred.text1, 2: pred.text2}
    if pred.polarity < 0: matches['a'] = 'not'
    relation = pred.relation
    sentence = pred.sentence
    lang = pred.language

    surface_forms = [SurfaceForm.get(matches[i], lang, auto_create=True)
                     for i in (1, 2)]
    concepts = [s.concept for s in surface_forms]
    
    # FIXME: english only so far
    freq = map_adverb(matches.get('a', ''))
    relation = Relation.objects.get(id=relation.id)
    frame, _ = Frame.objects.get_or_create(relation=relation, language=lang,
                                           text=frametext,
                                           defaults=dict(frequency=freq, 
                                                         goodness=1))
    frame.save()
    
    raw_assertion, _ = RawAssertion.objects.get_or_create(
        surface1=surface_forms[0],
        surface2=surface_forms[1],
        frame=frame,
        language=lang,
        creator=sentence.creator,
        defaults=dict(batch=batch))
    # still need to set assertion_id
    
    assertion, _ = Assertion.objects.get_or_create(
        relation=relation,
        concept1=concepts[0],
        concept2=concepts[1],
        frequency=freq,
        language=lang,
        defaults=dict(score=0)
    )
    #assertion.save()
    
    raw_assertion.assertion = assertion
    raw_assertion.sentence = sentence
    raw_assertion.save()

    sentence.set_rating(sentence.creator, 1, csamoa4_activity)
    raw_assertion.set_rating(sentence.creator, 1, csamoa4_activity)
    assertion.set_rating(sentence.creator, 1, csamoa4_activity)

    for rating in pred.rating_set.all():
        score = rating.rating_value.deltascore
        if score < -1: score = -1
        if score > 1: score = 1
        if rating.activity_id is None:
            rating_activity = Activity.objects.get(name='unknown')
        else:
            rating_activity = rating.activity
        sentence.set_rating(rating.user, score, rating_activity)
        raw_assertion.set_rating(rating.user, score, rating_activity)
        assertion.set_rating(rating.user, score, rating_activity)

    print '=>', unicode(assertion).encode('utf-8')
    return [assertion]

def run():
    #generator = yaml.load_all(open('delayed_test.yaml'))
    #all_entries = list(generator)

    activity_filter = Q()
    for actid in good_acts:
        activity_filter |= Q(sentence__activity__id=actid)
    return queryset_foreach(cn3.Predicate.objects.filter(activity_filter, language=en), process_predicate)

if __name__ == '__main__':
    user = User.objects.get(username='rspeer')
    status = run(user)

