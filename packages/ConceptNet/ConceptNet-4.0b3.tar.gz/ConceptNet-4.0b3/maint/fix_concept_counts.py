#!/usr/bin/env python

'''
Concepts keep track of their number of words. Or, they should.
'''

from csc.util import queryset_foreach

def fix_concept(concept):
    if concept.words: return
    concept.words = len(concept.text.split())
    concept.save()

queryset_foreach(Concept.objects.filter(language='en'), fix_concept)
