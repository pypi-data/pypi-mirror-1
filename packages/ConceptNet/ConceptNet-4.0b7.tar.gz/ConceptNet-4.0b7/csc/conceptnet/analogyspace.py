from divisi.labeled_tensor import SparseLabeledTensor
from conceptnet.models import Assertion, RelationType, Concept, Language
from math import log, sqrt
import logging

DEFAULT_IDENTITY_WEIGHT = sqrt(5)
DEFAULT_CUTOFF = 5

log_2 = log(2)

import re

###
### General utilities
###

relationtype_name_cache = None
def get_relationtype_names():
    global relationtype_name_cache
    if relationtype_name_cache is None:
        relationtype_name_cache = dict((x.id, x.name)
                                   for x in RelationType.objects.all())
    return relationtype_name_cache


def peopl_person(str, person_re = re.compile(r'\bpeopl\b')):
    '''Replace 'peopl' (the stemmed form) with 'person'.
    >>> peopl_person('peopl want')
    'person want'
    '''
    if not isinstance(str, basestring): return str
    return person_re.sub('person', str)


###
### Building AnalogySpace
###

def conceptnet_2d_from_db(lang,
                          identities=DEFAULT_IDENTITY_WEIGHT,
                          cutoff=DEFAULT_CUTOFF,
                          tuple=False):
    '''Builds a 2D conceptnet tensor from the database.'''
    if tuple: adder = addAssertionTuple
    else: adder = addAssertion
    return assertion_queryset_to_tensor(conceptnet_queryset(lang, cutoff), identities, adder)


def conceptnet_queryset(lang, cutoff):
    if isinstance(lang, Language): lang = lang.id
    return Assertion.objects.filter(language__id=lang,
                                    score__gt=0,
                                    concept1__num_predicates__gt=cutoff,
                                    concept2__num_predicates__gt=cutoff)

def addAssertion(tensor, relationtype, ltext, rtext, value):
    ltext = peopl_person(ltext)
    rtext = peopl_person(rtext)
    lprop = '%s/%s' % (ltext, relationtype)
    rprop = '%s/%s' % (relationtype, rtext)
    tensor[ltext, rprop] = value
    tensor[rtext, lprop] = value
    
def addAssertionTuple(tensor, relationtype, ltext, rtext, value):
    ltext = peopl_person(ltext)
    rtext = peopl_person(rtext)
    lprop = ('left',ltext, relationtype)
    rprop = ('right',rtext,relationtype)
    tensor[ltext, rprop] = value
    tensor[rtext, lprop] = value

def scorecurve(score):
    return log(max((score+1, 1)))/log_2

def assertion_queryset_to_tensor(queryset, identities, addToTensor=addAssertion):
    tensor = SparseLabeledTensor(ndim=2)
    
    relationtype_name = get_relationtype_names()
    for (reltype, concept1, concept2, score, polarity) in queryset.values_list(
        'relation_id', 'concept1__text',  'concept2__text',  'score', 'polarity'
        ).iterator():
        addToTensor(tensor, relationtype_name[reltype], concept1, concept2,
                    polarity*scorecurve(score))

    if identities:
        add_identities(tensor, identities)
    return tensor


def add_identities(tensor, weight=DEFAULT_IDENTITY_WEIGHT):
    logging.info('Adding identities, weight=%s', weight)
    for text in list(tensor.label_list(0)):
        lprop = text+'/InheritsFrom'
        rprop = 'InheritsFrom/'+text
        tensor[text, lprop] = weight
        tensor[text, rprop] = weight


#
# Experiment: an AnalogySpace from frames
#

def _conceptnet_2d_frames_from_db(queryset, identities):
    tensor = SparseLabeledTensor(ndim=2)
    
    relation_name = get_relationtype_names()
    for (rel, concept1, concept2, text1, text2, frame_id, score, polarity) in queryset.values_list(
        'relation_id', 'concept1__text',  'concept2__text', 'text1', 'text2', 'frame_id', 'score', 'polarity'
        ).iterator():
        val = polarity*scorecurve(score)
        # Raw
        addAssertionTuple(tensor, frame_id, text1, text2, val)
        # Assertion
        addAssertionTuple(tensor, relation_name[rel], concept1, concept2, val)
        # NormalizesTo
        addAssertionTuple(tensor, 'NormalizesTo', concept1, text1, 1)
        addAssertionTuple(tensor, 'NormalizesTo', concept2, text2, 1)
        addAssertionTuple(tensor, 'NormalizesTo', concept1, concept1, 1)
        addAssertionTuple(tensor, 'NormalizesTo', concept2, concept2, 1)

    if identities:
        add_identities(tensor, identities)
    return tensor

def conceptnet_2d_frames_from_db(lang,
                          identities=DEFAULT_IDENTITY_WEIGHT,
                          cutoff=DEFAULT_CUTOFF):
    return _conceptnet_2d_frames_from_db(conceptnet_queryset(lang, cutoff), identities)


#
# Experiment: Multilingual AnalogySpace
#

def conceptnet_multilingual(identities=DEFAULT_IDENTITY_WEIGHT, cutoff=DEFAULT_CUTOFF):
    tensor = SparseLabeledTensor(ndim=2)
    
    relationtype_name = get_relationtype_names()
    queryset = Assertion.objects.filter(score__gt=0,
                    concept1__num_predicates__gt=cutoff,
                    concept2__num_predicates__gt=cutoff)
    for (reltype, name1, name2, score, polarity, lang) in queryset.values_list(
        'relation_id', 'concept1__text',  'concept2__text',  'score', 'polarity', 'language_id').iterator():
        
        value = polarity*scorecurve(score)
        relationtype = relationtype_name[reltype]
        lconcept = (name1, lang)
        rconcept = (name2, lang)
        lfeature = (lconcept, relationtype)
        rfeature = (relationtype, rconcept)
        tensor[lconcept, rfeature] = value
        tensor[rconcept, lfeature] = value
        tensor[lconcept, ('InheritsFrom', lconcept)] = identities
        tensor[rconcept, ('InheritsFrom', rconcept)] = identities
    return tensor

#
# Experiment: One relation type at a time
#

def load_one_type(lang, relation,
                  identities=DEFAULT_IDENTITY_WEIGHT,
                  cutoff=DEFAULT_CUTOFF):
    queryset = conceptnet_queryset(lang, cutoff).filter(relation__id=relation)
    return assertion_queryset_to_tensor(queryset, identities)

def conceptnet_by_relations(lang, identities=0, cutoff=DEFAULT_CUTOFF):
    '''Returns a dictionary mapping names of relations to tensors of that kind of data.'''
    relationtype_name = get_relationtype_names()
    by_rel = [(relationtype_name[rel_id], load_one_type(lang, rel_id, identities, cutoff))
              for rel_id in relationtype_name.keys()
              if relationtype_name[rel_id] != 'InheritsFrom']
    return dict((name, tensor) for (name, tensor) in by_rel
                if len(tensor) > 0)

def identities_for_all_relations(byrel, weight=DEFAULT_IDENTITY_WEIGHT):
    tensor = SparseLabeledTensor(ndim=2)
    for other in byrel.itervalues():
        tensor._labels[0].extend(other._labels[0])
    add_identities(tensor, weight)
    return tensor

###
### Analysis helpers
###

def concept_similarity(svd, concept):
    concept = peopl_person(concept)
    return svd.u_distances_to(svd.weighted_u_vec(concept))

def predict_features(svd, concept):
    concept = peopl_person(concept)
    return svd.v_distances_to(svd.weighted_u_vec(concept))

def feature_similarity(svd, feature):
    return svd.v_distances_to(svd.weighted_v_vec(feature))

def predict_concepts(svd, feature):
    return svd.u_distances_to(svd.weighted_v_vec(feature))

def make_category(svd, concepts=[], features=[]):
    components = []
    from operator import add
    if len(concepts) > 0:
        components += [svd.weighted_u_vec(concept) for concept in concepts]
    if len(features) > 0:
        components += [svd.weighted_v_vec(feature) for feature in features]
    return reduce(add, components)


def category_similarity(svd, cat):
    '''Return all the features and concepts that are close to the given
    category, as (concepts, features), both labeled dense tensors.

    Example usage:
    concepts, features = category_similarity(svd, cat)
    concepts.top_items(10)
    features.top_items(10)'''
    return svd.u_distances_to(cat), svd.v_distances_to(cat)


def eval_assertion(svd, relationtype, ltext, rtext):
    ltext = peopl_person(ltext)
    rtext = peopl_person(rtext)
    lprop = '%s/%s' % (ltext, relationtype)
    rprop = '%s/%s' % (relationtype, rtext)

    # Evaluate right feature
    try:
        rprop_val = svd.get_ahat((ltext, rprop))
    except KeyError:
        rprop_val = 0

    # Evaluate left feature
    try:
        lprop_val = svd.get_ahat((rtext, lprop))
    except KeyError:
        lprop_val = 0

    return lprop_val, rprop_val


if __name__ == '__main__':
    import doctest
    doctest.testmod()

