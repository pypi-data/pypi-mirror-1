from django.db import models
from django.db.models import Q
from corpus.models import Language, Sentence, User, ScoredModel
from events.models import Event, Activity
from collections import defaultdict
from voting.models import Vote
from django.contrib.contenttypes import generic
from csc.util import cached

import re
from datetime import datetime

DEFAULT_LANGUAGE = en = Language(id='en', name='English') 

class TimestampedModel(models.Model):
    created = models.DateTimeField(default=datetime.now)
    updated = models.DateTimeField()
    
    def save(self, **kwargs):
        self.updated = datetime.now()
        super(TimestampedModel, self).save(**kwargs)

    class Meta:
        abstract = True

class UserData(TimestampedModel):
    user = models.ForeignKey(User)
    activity = models.ForeignKey(Activity)

class Batch(TimestampedModel):
    owner = models.ForeignKey(User)
    status = models.CharField(max_length=255,blank=True)
    remarks = models.TextField(blank=True)
    progress_num = models.IntegerField(default=0)
    progress_den = models.IntegerField(default=0)

    def __unicode__(self):
        return u"Batch " + str(self.id) + " (owner: " + self.owner.username + ") <" + str(self.progress_num) + "/" + str(self.progress_den) + " " + self.status + ">"

    class Meta:
        db_table = 'parsing_batch'

class Relation(models.Model):
    name = models.CharField(max_length=128,unique=True)
    description = models.CharField(max_length=-1, null=True, blank=True)

    def __unicode__(self):
        return self.name

    @classmethod
    def get(cls, name):
        return cls.objects.get(name=name)
    
    class Meta:
        db_table = 'predicatetypes'

class Frequency(models.Model):
    language = models.ForeignKey(Language)
    text = models.CharField(max_length=50, blank=True,
                            help_text='The frequency adverb used (e.g., "always", "sometimes", "never"). Empty means that the sentence has no frequency adverb.')
    # FIXME: is this help text still valid?
    value = models.IntegerField(help_text='A number between 0 and 100 indicating a rough numerical frequency to associate with this word. "always" would be 100, "never" would be 0, and not specifying a frequency adverb in English is somewhere around 60 or 70.')

    def __unicode__(self):
        return u'<%s: "%s" (%d)>' % (self.language.id, self.text, self.value)

    class Meta:
        unique_together = (('language', 'text'),)
        verbose_name = 'frequency adverb'
        verbose_name_plural = 'frequency adverbs'
        db_table = 'conceptnet_frequency'

class Frame(models.Model):
    language = models.ForeignKey(Language)
    text = models.TextField()
    relation = models.ForeignKey(Relation)
    goodness = models.IntegerField()
    frequency = models.ForeignKey(Frequency)
    question_yn = models.TextField(null=True, blank=True)
    question1 = models.TextField(null=True, blank=True)
    question2 = models.TextField(null=True, blank=True)

    def preferred(self):
        return self.goodness > 2
    preferred.boolean = True
    
    def fill_in(self, a, b):
        res = self.text.replace('{%}', '')
        res = res.replace('{1}', a, 1)
        return res.replace('{2}', b, 1)

    def __unicode__(self):
        return "%s (%s)" % (self.text, self.language.id)
    
    class Meta:
        db_table = 'conceptnet_frames'


class Feature(object):
    """
    Features are not models in the database, but they are useful ways to
    describe the knowledge contained in the edges of ConceptNet.

    A Feature is the combination of a :class:`Concept` and a :class:`Relation`.
    The combination of a Concept and a Feature, then, gives a
    :class:`Proposition`, a statement that can have a truth value; when given a
    truth value, this forms an :class:`Assertion`.

    As an example, the relation ``PartOf(cello, orchestra)`` breaks down into
    the concept ``cello`` and the feature ``PartOf(x, orchestra)``. It also
    breaks down into ``orchestra`` and ``PartOf(cello, x)``.

    Features can be *left features* or *right features*, depending on whether
    they include the left or right concept (that is, the first or second
    argument) in the Assertion. The Feature class itself is an abstract class,
    which is realized in the classes :class:`LeftFeature` and
    :class:`RightFeature`.
    
    Each Assertion can be described with its
    left concept (:attr:`concept1`) and its right feature, or its right concept
    (:attr:`concept2`) and its left feature.

    The notation is based on putting the relation in a "bucket". For
    example, ``PartOf(cello, orchestra) =
    cello\PartOf/orchesta``. Breaking this apart gives left and right
    features:

    cello: PartOf/orchestra (left concept and right feature)
    orchestra: cello\PartOf (right concept and left feature)
    """
    def __init__(self, relation, concept):
        if self.__class__ == Feature:
            raise NotImplementedError("Feature is an abstract class")
        if isinstance(relation, basestring):
            relation = Relation.objects.get(name=relation)
        #if isinstance(concept, basestring):
        #    concept = Concept.get(concept, auto_create=True)
        self.relation = relation
        self.concept = concept
        
    def to_tuple(self):
        return (self.tuple_key, self.relation.name, self.concept.text)
    @property
    def language(self):
        return self.concept.language
    def __hash__(self): # Features should be immutable.
        return hash((self.__class__.__name__, self.relation, self.concept))
    def __cmp__(self, other):
        if not isinstance(other, Feature): return -1
        return cmp((self.__class__, self.relation, self.concept),
                   (other.__class__, other.relation, other.concept))
    @staticmethod
    def from_tuple(tup, lang=DEFAULT_LANGUAGE):
        typ, rel, txt = tup
        c, _ = Concept.objects.get_or_create(text=txt, language=lang)
        r = Relation.objects.get(name=rel)
        classes = {'left': LeftFeature, 'right': RightFeature}
        if typ not in classes: raise ValueError
        return classes[typ](r, c)
    @property
    def frame(self):
        examples = self.matching_raw().filter(frame__goodness__gte=3)
        try:
            return examples[0].frame
        except IndexError:
            examples = self.matching_raw().filter(frame__goodness__gte=2)
            try:
                return examples[0].frame
            except IndexError:
                # If we can't find an example, just get the best frame
                return Frame.objects.filter(
                    language=self.language,
                    relation=self.relation
                ).order_by('-goodness')[0]
    def nl_statement(self, gap='...'):
        frame, ftext, text1, text2 = self.nl_parts(gap)
        return frame.fill_in(text1, text2)
    def _matching_assertions(self):
        return Assertion.objects.filter(
          language=self.concept.language,
          score__gt=0,
          relation=self.relation)
    def _matching_raw(self):
        return RawAssertion.objects.filter(
          language=self.concept.language,
          assertion__relation=self.relation)
    def nl_parts(self, gap='...'):
        frame = self.frame
        matching_raw = self.matching_raw()
        try:
            surface = matching_raw[0].surface(self.idx)
        except IndexError:
            surface = self.concept.some_surface() or self.concept
        if isinstance(self, LeftFeature):
            return (frame, frame.text, surface.text, gap)
        elif isinstance(self, RightFeature):
            return (frame, frame.text, gap, surface.text)
    def __repr__(self):
        return "<Feature: %s>" % unicode(self)
    
class LeftFeature(Feature):
    idx = 1
    tuple_key = 'left'
    def __unicode__(self):
        return '%s\\%s' % (self.concept.text, self.relation)
    def fill_in(self, newconcept):
        return Proposition(self.concept, self.relation, newconcept, self.concept.language)
    def matching_assertions(self):
        return self._matching_assertions().filter(concept1=self.concept)
    def matching_raw(self):
        return self._matching_raw().filter(surface1__concept=self.concept)

class RightFeature(Feature):
    idx = 2
    tuple_key = 'right'
    def __unicode__(self):
        return '%s/%s' % (self.relation, self.concept.text)
    def fill_in(self, newconcept):
        return Proposition(newconcept, self.relation, self.concept, self.concept.language)
    def matching_assertions(self):
        return self._matching_assertions().filter(concept2=self.concept)
    def matching_raw(self):
        return self._matching_raw().filter(assertion__concept2=self.concept)

def ensure_concept(concept):
    if isinstance(concept, Concept): return concept
    lang = DEFAULT_LANGUAGE
    if isinstance(concept, (tuple, list)):
        text, lang = concept
    else:
        text = concept
    return Concept.get(text, lang, auto_create=True)
    
class Proposition(object):
    def __init__(self, concept1, rel, concept2, lang):
        self.concept1 = ensure_concept(concept1)
        self.relation = rel
        self.concept2 = ensure_concept(concept2)
        self.lang = lang
    def __unicode__(self):
        return '<Proposition: %s %s %s>' % (self.concept1, self.relation,
        self.concept2)
    def nl_question(self):
        frame = Frame.objects.filter(language=self.lang, relation=self.relation,
                                     goodness__gte=3)[0]
        same_c1 = RawAssertion.objects.filter(language=self.lang,
            frame__relation=self.relation, surface1__concept=self.concept1)
        try:
            surface1 = same_c1[0].surface1.text
        except IndexError:
            surface1 = self.concept1.some_surface() or self.concept1
            surface1 = surface1.text
        same_c2 = RawAssertion.objects.filter(language=self.lang,
            frame__relation=self.relation, surface2__concept=self.concept2)
        try:
            surface2 = same_c2[0].surface2.text
        except IndexError:
            surface2 = self.concept2.some_surface() or self.concept2
            surface2 = surface2.text
        # The wiki-like brackets should be replaced by appropriate formatting.
        surface1b = "[[%s]]" % surface1
        surface2b = "[[%s]]" % surface2

        if frame.question_yn:
            return frame.question_yn.replace('{1}', surface1b)\
                   .replace('{2}', surface2b)
        else:
            return frame.text.replace('{1}', surface1b)\
                   .replace('{2}', surface2b)\
                   .replace('{%}', '') + '?'
    def right_feature(self):
        return RightFeature(self.relation, self.concept2)
    def left_feature(self):
        return LeftFeature(self.relation, self.concept1)
    def nl_parts(self):
        # TODO: replace this with something cleverer but still sufficiently
        # fast
        frame = Frame.objects.filter(language=self.lang,
        relation=self.relation, goodness__gte=3)[0]
        #surfaces = {}
        same_c1 = RawAssertion.objects.filter(frame__relation=self.relation,
                                              surface1__concept=self.concept1)
        try:
            surface1 = same_c1[0].surface1.text
        except IndexError:
            surface1 = self.concept1.some_surface() or self.concept1
            surface1 = surface1.text
        same_c2 = RawAssertion.objects.filter(language=self.lang,
            frame__relation=self.relation, surface2__concept=self.concept2)            
        try:
            surface2 = same_c2[0].surface2.text
        except IndexError:
            surface2 = self.concept2.some_surface() or self.concept2
            surface2 = surface2.text
        return (frame, frame.text, surface1, surface2)

    def nl_parts_topdown(self):
        frame = Frame.objects.filter(language=self.lang,
        relation=self.relation, goodness__gte=3)[0]
        #surfaces = {}
        same_c1 = RawAssertion.objects.filter(language=self.lang,
            frame__relation=self.relation, surface1__concept=self.concept1)
        try:
            surface1 = same_c1[0].surface1.text
        except IndexError:
            surface1 = self.concept1.some_surface() or self.concept1
            surface1 = surface1.text
        same_c2 = RawAssertion.objects.filter(language=self.lang,
            frame__relation=self.relation, surface2__concept=self.concept2)            
        try:
            surface2 = same_c2[0].surface2.text
        except IndexError:
            surface2 = self.concept2.some_surface() or self.concept2
            surface2 = surface2.text
        return (frame, frame.text, surface1, surface2)

class Concept(models.Model):
    """
    Concepts are the nodes of ConceptNet. They are the things that people have
    common sense knowledge about.
    
    Concepts are expressed in natural language with
    sets of related words and phrases: for example, "take a picture", "taking
    pictures", "to take pictures", and "you take a picture" are various
    `surface forms`_ of the same Concept.
    """
    language = models.ForeignKey(Language)
    text = models.TextField()
    num_assertions = models.IntegerField(default=0)
    # canonical_name = models.TextField()
    words = models.IntegerField(null=True)
    visible = models.BooleanField(default=False)

    @property
    @cached(lambda self: 'canonical_name_'+self.text, cached.minute)
    def canonical_name(self):
        return self.some_surface().text

    def __unicode__(self):
        return u"<" + self.language.id + ": " + self.text + ">"
    
    def get_assertions(self, useful_only=True):
        '''Get all :class:`Assertions` about this concept.'''
        return Assertion.get_filtered(Q(concept1=self) | Q(concept2=self), useful_only=useful_only)

    def get_assertions_forward(self, useful_only=True):
        '''Get all :class:`Assertions` with this concept on the left.'''
        return Assertion.get_filtered(Q(concept1=self), useful_only=useful_only)

    def get_assertions_reverse(self, useful_only=True):
        '''Get all :class:`Assertions` with this concept on the right.'''
        return Assertion.get_filtered(Q(concept2=self), useful_only=useful_only)

    def get_my_right_features(self, useful_only=True):
        '''
        Get all the RightFeatures that have been asserted about this concept.

        Returns a list of (feature, frequency, score, assertion) tuples.
        '''
        return [(RightFeature(a.relation, a.concept2), a.frequency, a.score, a)
                for a in self.get_assertions_forward(useful_only)]

    
    def get_my_left_features(self, useful_only=True):
        '''
        Get all the LeftFeatures that have been asserted about this concept.

        Returns a list of (feature, frequency, score, assertion) tuples.
        '''
        return [(LeftFeature(a.relation, a.concept1), a.frequency, a.score, a)
                for a in self.get_assertions_reverse(useful_only)]

    
    def group_assertions_by_feature(self, useful_only=True):
        forward_assertions = self.get_assertions_forward(useful_only)\
          .select_related('all_raw__surface2', 'frequency')
        reverse_assertions = self.get_assertions_reverse(useful_only)\
          .select_related('all_raw__surface1', 'frequency')
        thedict = {}
        for a in forward_assertions:
            # FIXME: seems that features no longer have polarity.
            thedict.setdefault(LeftFeature(a.relation, self, a.polarity), [])\
                .append((a.best_raw().surface2.text, a))
        for a in reverse_assertions:
            thedict.setdefault(RightFeature(a.relation, self, a.polarity), [])\
                .append((a.best_raw().surface1.text, a))
        return thedict
    
    def top_assertions_by_feature(self, limit=50, useful_only=True):
        results = []
        if useful_only: manager = Assertion.useful
        else: manager = Assertion.objects
        # forward relations
        for relation in Relation.objects.all():
            for polarity in (1,):
                feature = LeftFeature(relation, self, polarity)
                filtered = manager.filter(concept1=self, relation=relation)
                #if polarity == 1:
                #    filtered = filtered.filter(frequency__value__gte=0)
                #else:
                #    filtered = filtered.filter(frequency__value__lt=0)
                expanded = filtered.select_related('all_raw__surface2',
                                                   'frequency')
                best = expanded[:limit]
                described = [(a.best_raw().surface2.text, a.frequency.text,
                a.frequency.value > 0, a) for a in best]
                if len(described) > 0: results.append((feature, described))
        # backward relations
        for relation in Relation.objects.all():
            for polarity in (1,):
                feature = RightFeature(relation, self, polarity)
                filtered = manager.filter(concept2=self, relation=relation)
                #if polarity == 1:
                #    filtered = filtered.filter(frequency__value__gte=0)
                #else:
                #    filtered = filtered.filter(frequency__value__lt=0)
                expanded = filtered.select_related('all_raw__surface1',
                                                   'frequency')
                best = expanded[:limit]
                described = [(a.best_raw().surface1.text, a.frequency.text,
                a.frequency.value > 0, a) for a in best]
                if len(described) > 0: results.append((feature, described))
        results.sort(key=lambda x: -len(x[1]))
        return results

    def some_surface(self):
        """
        Get an arbitrary :class:`SurfaceForm` representing this concept.
        """
        try:
            return self.surfaceform_set.all()[0]
        except IndexError:
            return None
    
    @classmethod
    def get(cls, text, language, auto_create=False):
        """
        Get the Concept represented by a given string of text.

        If the Concept does not exist, this method will return None by default.
        However, if the parameter ``auto_create=True`` is given, then this will
        create the Concept (adding it to the database) instead.
        
        You should not run the string through a normalizer, or use a string
        which came from :attr:`Concept.text` (which is equivalent). If you
        have a normalized string, you should use :meth:`get_raw` instead.
        """
        if not isinstance(language, Language):
            language = Language.get(language)
        surface = SurfaceForm.get(text, language, auto_create)
        if surface is None:
            return Concept.get_raw(language.nl.normalize4(text), language)
        return surface.concept

    @classmethod
    def get_raw(cls, normalized_text, language, auto_create=False):
        """
        Get the Concept whose normalized form is the given string.

        If the Concept does not exist, this method will return None by default.
        However, if the parameter ``auto_create=True`` is given, then this will
        create the Concept (adding it to the database) instead.

        Normalized forms should not be assumed to be stable; they may change
        between releases.
        """
        if auto_create:
            concept_obj, created = cls.objects.get_or_create(text=normalized_text,language=language)
        else:
            concept_obj = cls.objects.get(text=normalized_text,language=language)
        return concept_obj

    class Meta:
        db_table = 'concepts'
        unique_together = ('language', 'text')

class UsefulAssertionManager(models.Manager):
    def get_query_set(self):
        return super(UsefulAssertionManager, self).get_query_set().filter(
            score__gt=0, concept1__visible=True, concept2__visible=True
        )

class Assertion(models.Model, ScoredModel):
    # Managers
    objects = models.Manager()
    useful = UsefulAssertionManager()
    
    language = models.ForeignKey(Language)
    relation = models.ForeignKey(Relation)
    concept1 = models.ForeignKey(Concept, related_name='left_assertion_set')
    concept2 = models.ForeignKey(Concept, related_name='right_assertion_set')
    score = models.IntegerField(default=0)
    frequency = models.ForeignKey(Frequency)
    votes = generic.GenericRelation(Vote)
    
    class Meta:
        db_table = 'assertions'
        unique_together = ('relation', 'concept1', 'concept2', 'frequency', 'language')
        ordering = ['-score']
        
    def best_raw(self):
        """
        Get the highest scoring :class:`RawAssertion` for this assertion.
        """
        return max(self.rawassertion_set.all(), key=lambda r: r.score)
        
    def nl_repr(self, wrap_text=lambda assertion, text: text):
        try:
            return self.best_raw().nl_repr(wrap_text)
        except ValueError:
            # FIXME: I'm sorry about this
            raise ValueError(str(self))
            return '%s %s %s' % (wrap_text(self, self.concept1.text),
                                 self.relation.name,
                                 wrap_text(self, self.concept2.text))
                          
    
    @property
    def creator(self):
        return self.best_raw().creator
        
    @property
    def polarity(self):
        if self.frequency.value >= 0: return 1
        else: return -1

    def __unicode__(self):
        return u"%s(%s, %s)[%s]" % (self.relation.name, self.concept1.text,
        self.concept2.text, self.frequency.text)
        
    @classmethod
    def get_filtered(cls, *a, **kw):
        useful_only = kw.pop('useful_only', True)
        if useful_only: return cls.useful.filter(*a, **kw)
        else: return cls.objects.filter(*a, **kw)

class SurfaceForm(models.Model):
    """
    A SurfaceForm is a string used to express a :class:`Concept` in its natural
    language.
    """
    language = models.ForeignKey(Language)
    concept = models.ForeignKey(Concept)
    text = models.TextField()
    residue = models.TextField()
    use_count = models.IntegerField(default=0)
    
    @staticmethod
    def get(text, lang, auto_create=False):
        if isinstance(lang, basestring):
            lang = Language.get(lang)
        nl = lang.nl
        try:
            known = SurfaceForm.objects.get(language=lang, text=text)
            return known
        except SurfaceForm.DoesNotExist:
            if not auto_create:
                return None
            else:
                lemma, residue = nl.lemma_factor(text)
                concept, created = Concept.objects.get_or_create(language=lang, text=lemma)
                if created: concept.save()

                surface_form = SurfaceForm.objects.create(concept=concept,
                text=text, residue=residue, language=lang)
                return surface_form
    
    def __unicode__(self):
        return self.text
    
    class Meta:
        db_table = 'surface_forms'
        ordering = ['-use_count']

class RawAssertion(TimestampedModel, ScoredModel):
    sentence = models.ForeignKey(Sentence, null=True)
    assertion = models.ForeignKey(Assertion, null=True)
    creator = models.ForeignKey(User)
    surface1 = models.ForeignKey(SurfaceForm, related_name='left_rawassertion_set')
    surface2 = models.ForeignKey(SurfaceForm, related_name='right_rawassertion_set')
    frame = models.ForeignKey(Frame)    
    batch = models.ForeignKey(Batch, null=True)
    language = models.ForeignKey(Language)
    score = models.IntegerField(default=0)
    votes = generic.GenericRelation(Vote)

    @property
    def relation(self): return self.frame.relation
    @property
    def text1(self): return self.surface1.text
    @property
    def text2(self): return self.surface2.text
    
    def __unicode__(self):
        return u"%(language)s: ('%(text1)s' %(relation)s '%(text2)s') s=%(score)d" % dict(
            language=self.language.id, relation=self.relation.name,
            text1=self.text1, text2=self.text2, score=self.score)

    def nl_repr(self, wrap_text=lambda assertion, text: text):
        """Reconstruct the natural language representation.
        The text concepts are passed to the wrap_text function to
        allow a view to wrap them in a link (or do any other
        transformation. The prototype for wrap_text is:

        wrap_text(assertion, text)

        where ``assertion`` is this RawAssertion object and ``text`` is the
        natural-language text of the concept (text1 or text2)."""

        text1 = wrap_text(self, self.surface1.text.strip())
        text2 = wrap_text(self, self.surface2.text.strip())
        return self.frame.fill_in(text1, text2)
        
    def main_sentence(self):
        return self.sentence
        #return self.sentences.all()[0]

    def surface(self, idx):
        """Get either surface1 or surface2, depending on the (1-based) idx."""
        if idx == 1: return self.surface1
        elif idx == 2: return self.surface2
        else: raise KeyError(idx)
    
    @staticmethod
    def make(user, frame, text1, text2, activity, vote=1):
        """
        Create a RawAssertion and a corresponding :class:`Assertion`
        and :class:`Sentence` from user input. Assign votes appropriately.
        
        Requires the following arguments:
        
        - *user*: The user to credit the new assertion to.
        - *frame*: The :class:`Frame` that is being filled in.
        - *text1*: A string filling the first slot of the frame.
        - *text2*: A string filling the second slot of the frame.
        - *activity*: The event that produced this assertion.
        - *vote*: The user's vote on the assertion (often +1, but -1 can occur
          when the user is answering "no" to a question that has not been
          answered before).
        """
        assert text1 != text2
        lang = frame.language
        surface1 = SurfaceForm.get(text1, lang, auto_create=True)
        surface2 = SurfaceForm.get(text2, lang, auto_create=True)
        
        raw_assertion, _ = RawAssertion.objects.get_or_create(
            frame=frame,
            surface1=surface1,
            surface2=surface2,
            language=lang,
            creator=user,
            defaults=dict(score=0)
        )
        
        assertion, _ = Assertion.objects.get_or_create(
            relation=frame.relation,
            concept1=surface1.concept,
            concept2=surface2.concept,
            frequency=frame.frequency,
            language=lang,
            defaults=dict(score=0)
        )
        
        sentence, _ = Sentence.objects.get_or_create(
            text=frame.fill_in(text1, text2),
            creator=user,
            language=lang,
            activity=activity,
            defaults=dict(score=0)
        )
                
        Event.record_event(sentence, user, activity)
        sentence.set_rating(user, vote, activity)
        raw_assertion.set_rating(user, vote, activity)
        assertion.set_rating(user, vote, activity)
        
        raw_assertion.assertion = assertion
        raw_assertion.sentence = sentence
        raw_assertion.save()
        return raw_assertion
        
    class Meta:
        db_table = 'raw_assertions'
        ordering = ['-score']


class Rating(UserData):
    sentence = models.ForeignKey(Sentence, blank=True, null=True)
    raw_assertion = models.ForeignKey(RawAssertion, blank=True, null=True)
    assertion = models.ForeignKey(Assertion, blank=True, null=True)
    # already in UserData
    # activity = models.ForeignKey(Activity, null=True)
    old_rating_id = models.IntegerField(blank=True, null=True)
    score = models.IntegerField()
 
    def __unicode__(self):
        return 'FIXME'

    class Meta:
        db_table = 'ratings'


