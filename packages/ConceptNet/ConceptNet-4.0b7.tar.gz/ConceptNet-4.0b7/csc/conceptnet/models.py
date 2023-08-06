# Models for ConceptNet

from django.db import models
from django.db.models import Q
from corpus.models import Language, Sentence, User
from events.models import Activity

import re
from datetime import datetime

# TODO:
# - documentation

class AliasDescriptor(property):
    '''Allows an attribute to appear under another name.'''
    def __init__(prop, name):
        super(AliasDescriptor, prop).__init__(prop.getter, prop.setter)
        prop.name = name

    def getter(prop, self):
        return getattr(self, prop.name)

    def setter(prop, self, val):
        return setattr(self, prop.name, val)
    

class Relation(models.Model):
    name = models.CharField(max_length=128,unique=True)
#   preferred_frame = models.ForeignKey('Frame')
    description = models.CharField(max_length=100)
    generalize_on = models.IntegerField(default=0)

    def __unicode__(self):
        return self.name
    
    def preferred_frame(self, lang):
        try:
            return Frame.objects.filter(relation=self, goodness=3, language=lang)[0]
        except IndexError:
            raise ValueError, "no preferred frame"

    class Meta:
        db_table = 'predicatetypes'

# old names
PredicateType = RelationType = Relation


class Frequency(models.Model):
    language = models.ForeignKey(Language)
    text = models.CharField(max_length=50, blank=True,
                            help_text='The frequency adverb used (e.g., "always", "sometimes", "never"). Empty means that the sentence has no frequency adverb.')
    value = models.IntegerField(help_text='A number between 0 and 100 indicating a rough numerical frequency to associate with this word. "always" would be 100, "never" would be 0, and not specifying a frequency adverb in English is somewhere around 60 or 70.')

    def __unicode__(self):
        return u'<%s: "%s" (%d)>' % (self.language.id, self.text, self.value)

    class Meta:
        unique_together = (('language', 'text'),)
        verbose_name = 'frequency adverb'
        verbose_name_plural = 'frequency adverbs'


class Frame(models.Model):
    relation = models.ForeignKey(PredicateType, db_column='predtype_id', verbose_name="relation type")
    text = models.TextField()
    language = models.ForeignKey(Language)

    goodness = models.IntegerField(help_text='Quality of the frame. 3=preferred, 2=acceptable, 1=poor')
    frequency = models.ForeignKey(Frequency)
    should_translate = models.BooleanField('should be translated', default=True)

    # Unused stuff:
    type1 = models.TextField(blank=True)
    type2 = models.TextField(blank=True)
    oldid = models.IntegerField(null=True)
    text_question1 = models.TextField(blank=True)
    text_question2 = models.TextField(blank=True)
    text_question_yn = models.TextField(blank=True)
    pattern_id = models.IntegerField(null=True)
    preferred_frame = models.ForeignKey('self', null=True)
    comparison = models.CharField(max_length=-1)
    
    def preferred(self):
        return self.goodness > 2
    preferred.boolean = True

    def __unicode__(self):
        return u"<%s: %s>" % (self.language.id, self.text)
# + "', " + self.type1 + ", " + self.type2 + ">"

    def fill_in(self, a, b):
        try:
            res = self.text.replace('{1}', a, 1)
            return res.replace('{2}', b, 1).replace('{%}', '')
        except:
            return ''

    class Meta:
        db_table = 'frames'
        ordering = ['-goodness']


class Batch(models.Model):
    owner = models.ForeignKey(User)
    created = models.DateTimeField(default=datetime.now)
    updated = models.DateTimeField()
    status = models.CharField(max_length=255,blank=True)
    remarks = models.TextField(blank=True)
    progress_num = models.IntegerField(default=0)
    progress_den = models.IntegerField(default=0)

    def save(self):
        self.updated = datetime.now()
        super(Batch, self).save()

    def __unicode__(self):
        return u"Batch " + str(self.id) + " (owner: " + self.owner.username + ") <" + str(self.progress_num) + "/" + str(self.progress_den) + " " + self.status + ">"

    class Meta:
        db_table = 'parsing_batch'


class RawAssertion(models.Model):
    batch = models.ForeignKey(Batch)
    frame = models.ForeignKey(Frame)
    relation = models.ForeignKey(PredicateType, db_column='predtype_id')
    text1 = models.TextField()
    text2 = models.TextField()
    polarity = models.IntegerField()
    modality = models.IntegerField()
    sentence = models.ForeignKey(Sentence)
    language = models.ForeignKey(Language)
    predicate = models.ForeignKey('Assertion',related_name='all_raw', null=True)
    depth = models.IntegerField(default=0)

    def __unicode__(self):
        return u"(" + self.language.id + ") (" + self.relation.name + " '" + self.text1 + "' '" + self.text2 + "' \"d=" + str(self.depth) + ";p=" + str(self.polarity) + "\")"
    
    def nl_repr(self, wrap_text=lambda assertion, text: text):
        """Reconstruct the natural language representation.
        The text concepts are passed to the wrap_text function to
        allow a view to wrap them in a link (or do any other
        transformation. The prototype for wrap_text is:

        wrap_text(assertion, text)

        where assertion is this RawAssertion object and text is the
        natural-language text of the concept (text1 or text2)."""

        text1 = wrap_text(self, self.text1.strip())
        text2 = wrap_text(self, self.text2.strip())

        frame = self.frame.text
        frame = frame.replace('{1}', text1)
        frame = frame.replace('{2}', text2)

        # Handle negation. Except don't.
        if False and self.polarity == -1:
            if frame.find('{%}') == -1:
                # FIXME HACK Rubyism: a negated frame doesn't count
                if frame.find("n't") == -1 and frame.find("not") == -1:
                    # FIXME: Hard-coded English phrase!
                    frame = 'It is not true that '+ frame
            else:
                # FIXME: Hard-coded English phrase!
                frame = frame.replace('{%}', 'not ')
        else:
            frame = frame.replace('{%}', '')

        return frame

    class Meta:
        db_table = 'parsing_rawpredicate'

RawPredicate = RawAssertion

# FIXME: hardcoded English!
# (at least it doesn't break other languages...)
negated_re = re.compile(r'(\bnot\b)|(n\'t\b)|(\bno\b)')

class Concept(models.Model):

    language = models.ForeignKey(Language)
    text = models.TextField()
    num_predicates = models.IntegerField(default=0) # FIXME: old name
    words = models.IntegerField()
    cached_name = models.TextField()

    # Unused:
    last_update = models.DateTimeField()
    last_inference = models.DateTimeField()
    active = models.BooleanField()

    def __unicode__(self):
        return u"<" + self.language.id + ": " + self.text + ">"

    def get_assertions(self, useful_only=True):
        '''Get all assertions about this concept.'''
        conditions = Q(concept1=self) | Q(concept2=self)
        if useful_only:
            return Assertion.useful.filter(conditions)
        else:
            return Assertion.objects.filter(conditions)

    def get_fwd_relations(self):
        '''Get all forward relations from this concept
        A forward relation is an assertion with this concept
        as its first entry.

        Adds an "other" field, for the other concept.
        Returns a genarator expression.'''
        # TODO: port this to a QuerySet subclass to add the 'other'.
        def with_other(assertion):
            assertion.other = assertion.concept2
            return assertion
        return (with_other(assertion) for assertion in self.fwd_relations.all())

    def get_rev_relations(self):
        '''Get all reverse relations from this concept.
        A reverse relation is a relation with this concept
        as its second entry.'''
        def with_other(assertion):
            assertion.other = assertion.concept1
            return assertion
        return (with_other(assertion) for assertion in self.rev_relations.all())

    def get_nlrepr_all(self):
        reprs = {}
        for p in self.fwd_relations.values('text1'):
            reprs.setdefault(p['text1'], 0)
            reprs[p['text1']] += 1
        for p in self.rev_relations.values('text2'):
            reprs.setdefault(p['text2'], 0)
            reprs[p['text2']] += 1
        # FIXME: use key= parameter instead.
        decorated = [(x[1], x[0]) for x in reprs.items()]
        decorated.sort(reverse=True)
        return [r[-1] for r in decorated]

    def get_nlrepr_most_common(self):
        return self.get_nlrepr_all()[0]

    @property
    def canonical_name(self):
        if not self.cached_name:
            # Simple algorithm loosely based off of Rob's
            reprs = self.get_nlrepr_all()
            if len(reprs) == 0: return ''
            def len_penalize_negation(x):
                if negated_re.search(x):
                    return 100 + len(x)
                else:
                    return len(x)
            reprs.sort(key=len_penalize_negation)
            self.cached_name = reprs[0]
            self.save()

        return self.cached_name

    @classmethod
    def get(cls, text, language, auto_create=False):
        if not isinstance(language, Language):
            language = Language.get(language)
        return cls.get_raw(language.nl.normalize(text), language, auto_create)

    @classmethod
    def get_raw(cls, normalized_text, language, auto_create=False):
        if auto_create:
            concept_obj, created = cls.objects.get_or_create(text=normalized_text,language=language)
        else:
            concept_obj = cls.objects.get(text=normalized_text,language=language)
        return concept_obj
    
    class Meta:
        db_table = 'stems'
        unique_together = (('text','language',),)

# old name
Stem = Concept


class UsefulAssertionManager(models.Manager):
    def get_query_set(self):
        return super(UsefulAssertionManager, self).get_query_set().filter(score__gt=0, visible=True)


class Assertion(models.Model):
    # Managers
    objects = models.Manager()
    useful = UsefulAssertionManager()

    # Keys
    batch = models.ForeignKey(Batch)
    # This should really be a one-to-one relationship:
    raw = models.ForeignKey(RawAssertion,related_name='raw_as_canonical')
    frame = models.ForeignKey(Frame)

    relation = models.ForeignKey(Relation, db_column='predtype_id')
    concept1 = models.ForeignKey(Concept,related_name='fwd_relations', db_column='stem1_id')
    concept2 = models.ForeignKey(Concept,related_name='rev_relations', db_column='stem2_id')
    stem1 = AliasDescriptor('concept1')
    stem2 = AliasDescriptor('concept2')

    polarity = models.IntegerField(default=1)
    modality = models.IntegerField(default=6)
    score = models.IntegerField(default=0)

    created_on = models.DateTimeField(default=datetime.now)

    # Compatibility members
    text1 = models.TextField()
    text2 = models.TextField()
    creator = models.ForeignKey(User)
    sentence = models.ForeignKey(Sentence)
    language = models.ForeignKey(Language, db_column='language_id')
    visible = models.BooleanField()

    test_group = models.IntegerField()

    def nl_repr(self, wrap_text=lambda assertion, text: text):
        return self.raw.nl_repr(wrap_text)

    @staticmethod
    def recently_learned(lang='en', n=10):
        return Assertion.useful.filter(language=lang) \
            .order_by('-created_on')[:n]


    @classmethod
    def from_frame(klass, user, frame, text1, text2, activity, batch, rating_value):
        # Extract language
        lang = frame.language

        # Extract concepts
        concept1 = Concept.get(text1, lang, auto_create=True)
        concept2 = Concept.get(text2, lang, auto_create=True)

        # Build sentence
        text = re.sub(r'\{1\}', text1, frame.text)
        text = re.sub(r'\{2\}', text2, text)
        # FIXME: temporary hack
        text = re.sub(r'\{%\}', '', text)
        # FIXME: don't create these yet; wait till the master save.
        sent = Sentence.objects.create(
            text=text,
            creator=user,
            language=lang,
            activity=activity)

        # Build a raw assertion
        raw_pred = RawAssertion.objects.create(
            frame=frame,
            relation=frame.relation,
            text1=text1, text2=text2,
            # FIXME: polarity should be taken from the frame
            polarity=1, modality=6,
            sentence=sent, language=lang,
            batch=batch)

        # Build a assertion.
        # Only the relation and concepts are unique.
        pred, created = klass.objects.get_or_create(
            relation=frame.relation,
            concept1=concept1, concept2=concept2,
            # FIXME: should we update any of this info?
            defaults=dict(
                frame=frame,
                polarity=raw_pred.polarity,
                modality=raw_pred.modality,
                text1=text1,
                text2=text2,
                creator=user,
                sentence=sent,
                language=lang,
                visible=True,
                batch=batch))

        if pred.raw_id is None:
            pred.raw = raw_pred
            pred.save()

        raw_pred.predicate_id = pred.id
        raw_pred.save()

        if created:
            # Increment concept usage counts
            concept1.num_predicates += 1
            concept2.num_predicates += 1
            concept1.save()
            concept2.save()

        pred.rate(user, rating_value, activity)

        # Operation Complete!
        return pred

    def get_rating(self, user):
        '''get_rating(user)
        Retrieve the rating object, if one exists, for a user-assertion pair.
        If no such object exists, return None.
        Silently removes extraneous ratings.'''

        ratings = list(self.rating_set.filter(user=user).order_by('id'))

        # Remove extraneous ratings
        for extra in ratings[:-1]: extra.delete()

        # Abort if no ratings remain
        if len(ratings) == 0: return None

        # Operation Complete!
        return ratings[0]

    def rate(self, user, rating_value, activity=None):
        '''rate(user, rating_value)
        Reflect that the given user rated this assertion with
        the given rating value. If rating_value is None, remove
        any existing rating.

        This function ensures that the score equals the sum of
        all ratings, and that a user can only rate an assertion
        once. (Extra ratings are silently removed.)'''

        old_rating = self.get_rating(user)
        if rating_value is None:
            # Clear all ratings if rating_value is None.
            if old_rating is not None: old_rating.delete()
        else:
            if old_rating is None:
                self.rating_set.add(Rating(
                        user=user,
                        rating_value=rating_value,
                        activity=activity))
            else:
                # Update the rating.
                old_rating.rating_value = rating_value
                old_rating.activity = activity
                old_rating.save()

        self.update_score()


    def update_score(self):
        # FIXME: Race condition.
        self.score = sum([rating.rating_value.deltascore
                          for rating in self.rating_set.all()])
        self.save()

    def __unicode__(self):
        return u'(%s(%s, %s), p=%s;m=%s;s=%s)' % (
            self.relation,
            self.concept1, self.concept2,
            self.polarity, self.modality,
            self.score)

    class Meta:
        db_table = 'predicates'
        ordering = ['-score']
        unique_together = (('relation', 'concept1', 'concept2'),)

Predicate = Assertion


class RatingValue(models.Model):
    label = models.CharField(max_length=255)
    deltascore = models.IntegerField()
    modality = models.IntegerField()
    positive = models.BooleanField(default=True)
    negative = models.BooleanField(default=False)

    usertest = models.BooleanField()
    eval_score = models.IntegerField()
    
    def __unicode__(self):
        return u'<rating_value:"' + self.label + '"' + \
            ' delta:' + str(self.deltascore) + \
            ' "p=' + str(self.positive) + \
            ';n=' + str(self.negative) + \
            ';m=' + str(self.modality) + '">'

    class  Meta:
        db_table = 'commons_rating_values'
        ordering = ['modality']


class Rating(models.Model):
    user = models.ForeignKey(User, db_column='user_id')
    statement = models.ForeignKey(Assertion)
    type = models.CharField(max_length=255,default='Predicate')
    rating_value = models.ForeignKey(RatingValue)
    activity = models.ForeignKey(Activity)
    updated_on = models.DateTimeField()

    def save(self):
        self.updated_on = datetime.now()
        super(Rating, self).save()

    def __unicode__(self):
        return u'<rating: %s user: "%s" value: "%s">' % (
            self.statement,
            self.user,
            self.rating_value.label)

    class Meta:
        db_table = 'commons_ratings'
