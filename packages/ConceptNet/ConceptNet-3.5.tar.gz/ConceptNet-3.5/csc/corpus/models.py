__version__ = "4.0"
__author__ = "kcarnold@media.mit.edu, rspeer@media.mit.edu, jalonso@media.mit.edu, havasi@media.mit.edu, hugo@media.mit.edu"
__url__ = 'conceptnet.media.mit.edu'
from django.db import models
from django.contrib.auth.models import User
from django.utils.functional import memoize
from datetime import datetime
from voting.models import Vote
from events.models import Event, Activity
from django.contrib.contenttypes import generic

import re

class ScoredModel(object):
    def get_rating(self, user):
        return getattr(Vote.objects.get_for_user(self, user), 'vote', None)

    def set_rating(self, user, val, activity):
        Vote.objects.record_vote(self, user, val)
        Event.record_event(self, user, activity)
        self.update_score()

    def update_score(self):
        self.score = Vote.objects.get_score(self)['score']
        self.save()


cached_nl = {}
def get_nl(lang_code):
    """
    Get an object that handles natural language operations for a given
    language, and remember it so that it doesn't have to be looked up again.
    """
    name = 'nl.'+lang_code
    return __import__(name, [], [], 'NL').NL()
get_nl = memoize(get_nl, cached_nl, 1)

cached_langs = {}
def get_lang(lang_code):
    """
    Get a Language instance for a particular language, and remember it so that
    it doesn't have to be looked up again.
    """
    return Language.objects.get(id=lang_code)
get_lang = memoize(get_lang, cached_langs, 1)

class Language(models.Model):
    """
    A database object representing a language.

    Instances of Language can be used in filter expressions to select only
    objects that apply to a particular language. For example:
    >>> en = Language.get('en')
    >>> english_sentences = Sentence.objects.filter(language=en)
    """
    id = models.CharField(max_length=16,primary_key=True)
    name = models.TextField(blank=True)
    def __str__(self):
        return "%s (%s)" % (self.name, self.id)

    @staticmethod
    def get(id):
        """
        Get a language from its ISO language code.
        """
        if isinstance(id,Language): return id
        return get_lang(id)

    @property
    def nl(self):
        """
        A collection of natural language tools for a language.
        """
        return get_nl(self.id)

class Sentence(models.Model, ScoredModel):
    """
    A statement entered by a contributor, in unparsed natural language.
    """
    text = models.TextField(blank=False)
    creator = models.ForeignKey(User)
    created_on = models.DateTimeField(default=datetime.now)
    language = models.ForeignKey(Language)
    activity = models.ForeignKey(Activity)
    score = models.IntegerField(default=0)
    votes = generic.GenericRelation(Vote)

    def __unicode__(self):
        return  u'<' + self.language.id + u': ' + \
                u'"' + self.text + u'"' + \
                u'(by:' + unicode(self.creator_id) + \
                u' activity:' + self.activity.name + \
                u')>'
    
    def set_rating(self, user, val, activity):
        Vote.objects.record_vote(self, user, val)
        Event.record_event(self, user, activity)
        self.score += val
        self.save()

    class Meta:
        db_table = 'sentences'

class TaggedSentence(models.Model):
    """
    The results of running a sentence through a tagger such as MXPOST.

    We could use this as a step in parsing ConceptNet, but we currently don't.
    """
    text = models.TextField()
    language = models.ForeignKey(Language)
    sentence = models.ForeignKey(Sentence, primary_key=True)
    
    def tagged_words(self):
        for part in self.text.split(" "):
            word, tag = part.rsplit("/", 1)
            yield word, tag
    
    def __unicode__(self):
        return self.text
    
    class Meta:
        db_table = 'tagged_sentences'

class DependencyParse(models.Model):
    """
    Each instance of DependencyParse is a single link in the Stanford
    dependency parse of a sentence.
    """
    sentence_id = models.IntegerField()
    linktype = models.CharField(max_length=20)
    word1 = models.CharField(max_length=100)
    word2 = models.CharField(max_length=100)
    index1 = models.IntegerField()
    index2 = models.IntegerField()
    
    _PARSE_RE = re.compile(r"(.+)\((.*)-(\d+)'*, (.*)-(\d+)'*\)")
    
    @staticmethod
    def from_string(sentence_id, depstring):
        try:
            link, w1, i1, w2, i2 = DependencyParse._PARSE_RE.match(depstring).groups()
        except AttributeError:
            raise ValueError("didn't match regex pattern: %s" % depstring)
        dep_obj = DependencyParse(sentence_id=sentence_id, linktype=link,
                                  word1=w1, index1=int(i1),
                                  word2=w2, index2=int(i2))
        return dep_obj

    def __unicode__(self):
        return u'%s(%s_%d, %s_%d) (sent %d)' % (
            self.linktype, self.word1, self.index1, self.word2, self.index2,
            self.sentence_id)
    
    class Meta:
        db_table = 'dependency_parses'

class AutoreplaceRule(models.Model):
    language = models.ForeignKey(Language)
    family = models.CharField(blank=False,max_length=128)
    match = models.CharField(blank=False,max_length=128)
    replace_with = models.CharField(blank=True,max_length=128)
    unique_together = (('language', 'family', 'match'),)

    def __str__(self):
        return " (" + str(self.language.id) + ") " + self.family + " [" + self.match + " => " + self.replace_with + "]"

    class Autoreplacer:
        def __init__(self,kb,language,family):
            self.language = language
            self.kb = kb
            self.family = family

        def __str__(self):
            return "(" + str(self.language.id) +") " + self.family + " autoreplace KB"

        def __call__(self, text):
            toks = text.split()
            toks = [self.kb.get(x,x) for x in toks]
            return ' '.join(toks)

    @staticmethod
    def build_autoreplacer(language,family):
        kb = {}
        for rule in language.autoreplacerule_set.filter(family=family):
            kb[rule.match] = rule.replace_with
        return AutoreplaceRule.Autoreplacer(kb,language,family)

    class Admin:
        pass

class PartOfSpeech(models.Model):
    """
    A part of speech that can be detected with a Lemmatizer.
    """
    symbol = models.CharField(max_length=4)
    priority = models.IntegerField(blank=False, default=0)
    class Meta:
        db_table = 'lemma_pos'
        
    def __str__(self):
        return self.symbol

class Inflection(models.Model):
    """
    An inflection that can be separated from the base of a word by a
    Lemmatizer.

    The symbol field is arbitrary, but we prefer it to be compositional
    wherever possible -- for example, present tense inflections should all have
    the character 'e' in them.
    """
    symbol = models.CharField(max_length=4)
    description = models.CharField(max_length=128, default='')
    class Meta:
        db_table = 'lemma_infl'
    
    def __str__(self):
        return "%s (%s)" % (self.description, self.symbol)

class Lemmatizer(object):
    "Experimental."
    def __init__(self, cls):
        self.cache = {}
        self.pos_list = list(PartOfSpeech.objects.all().order_by("priority"))
        for lemma in cls.objects.all():
            self.cache[(lemma.word, lemma.pos.symbol, lemma.language.id)]\
              = (lemma.lemma, lemma.inflection)
            reverse = (lemma.lemma, lemma.pos.symbol, lemma.inflection.symbol,
            lemma.language.id)
            if reverse not in cache:
                self.cache[reverse] = lemma.word

    def lookup(self, word, language):
        # TODO: account for string format as opposed to Django objects
        for pos in pos_list:
            if (word, pos, language) in self.cache:
                lemma, infl = self.cache[word, pos, language]
                return (lemma, pos, infl)
        return None
    
    def lemma_split(word, language):
        # TODO: use strings
        if isinstance(language, basestring):
            language = Language.get(language)
        lemma_word, pos, inflection = self.lookup(word, language)
        inflectstr = self.inflect('+', pos, inflection, language)[0]
        if inflectstr == '+': inflectstr = ''
        return lemma_word, inflectstr
    
    def inflect(self, lemma, pos, inflection, language):
        # TODO: use strings
        if isinstance(language, basestring):
            language = Language.get(language)
        if isinstance(pos, basestring):
            pos = PartOfSpeech.objects.get(symbol=pos)
        if isinstance(inflection, basestring):
            inflection = Inflection.objects.get(symbol=inflection, language=language)
        lookup = '^'+lemma
        found = Lemma.objects.none()
        while found.count() == 0:
            found = Lemma.objects.filter(lemma=lookup, pos=pos,
                                         inflection=inflection,
                                         language=language
                                         ).order_by('pos__priority')
            if len(lookup) == 0 and found.count() == 0: return [lemma]
            lookup = lookup[1:]
        result = []
        for entry in found:
            removechars = len(entry.lemma.strip('^'))
            word = lemma[0:len(lemma)-removechars] + entry.word.strip('^')
            result.append(word)
        return result
    def lemma_factor(self, text, keep_stopwords=False):
        # TODO: use strings
        if not isinstance(text, unicode): text = text.decode('utf-8')
        punct = string.punctuation.replace("'", "").replace('-', '')
        
        words = text.replace('/', ' ').split()
        words = [w.strip(punct).lower() for w in words]
        words = [self.autocorrect.get(word, word) for word in words]
        lemma_tuples = [Lemma.lemma_split(word, self.lang) for word in words]
        lemmas_pre = []
        residue_pre = []
        lemma_index = 0
        for i in range(len(words)):
            if not keep_stopwords and lemma_tuples[i][0] in self.stopwords:
                residue_pre.append((None, words[i]))
            else:
                lemmas_pre.append((lemma_tuples[i][0], lemma_index))
                residue_pre.append((lemma_index, lemma_tuples[i][1]))
                lemma_index += 1
        #lemmas_pre.sort()
        permute = [l[1] for l in lemmas_pre]
        invpermute = [permute.index(i) for i in range(len(permute))]
        lemmas = [l[0] for l in lemmas_pre]
        lemmas = [self.swapdict.get(lemma, lemma) for lemma in lemmas]

        residue = []
        for lemma_index, text in residue_pre:
            if lemma_index is None: residue.append(text)
            else: residue.append(str(invpermute[lemma_index]+1) + text)
        if len(lemmas) == 0 and not keep_stopwords:
            return self.lemma_factor(text, keep_stopwords=True)
        return (u' '.join(lemmas), u' '.join(residue))

class Lemma(models.Model):
    """
    A Lemma entry specifies how to lemmatize a pattern of words. For example,
    it might specify that you pluralize the ending 'f' to 'ves'.
    """
    language = models.ForeignKey(Language)
    word = models.CharField(max_length=128)
    lemma = models.CharField(max_length=128)
    pos = models.ForeignKey(PartOfSpeech)
    inflection = models.ForeignKey(Inflection)
    unique_together = (('language', 'word', 'lemma', 'pos', 'inflection'),)
    lemmatizer = None

    @staticmethod
    def lemmatize_cache_doesntwork(word, language):
        """
        Get the lemma form of a word, as well as a list of
        (part_of_speech, inflection) pairs that tell you how to construct
        another word like it.
        """
        
        # If the language was a string like 'en', get the language object.
        if isinstance(language, basestring):
            language = Language.get(language)
            
        # ^ is the "start of word" marker.
        lookup = '^'+word
        
        # Look for this word in our lemma database, starting from the whole
        # word and gradually removing letters. The point is to find the longest
        # suffix of the word that we know how to handle.        
        found = None
        while found is None:
            found = lemmatizer.lookup(lookup, language)
            if len(lookup) == 0 and found is None: return (word, [])
            lookup = lookup[1:]

        word, lemma, pos, infl = found
        removechars = len(word.strip('^'))
        lemmaword = word[0:len(word)-removechars] + lemma.strip('^')
        return [lemmaword, (pos, infl)]
    
    @staticmethod
    def lemmatize(word, language):
        """
        Get the lemma form of a word, as well as a list of
        (part_of_speech, inflection) pairs that tell you how to construct
        another word like it.
        """
        
        # If the language was a string like 'en', get the language object.
        if isinstance(language, basestring):
            language = Language.get(language)
            
        # ^ is the "start of word" marker.
        lookup = '^'+word
        
        # Look for this word in our lemma database, starting from the whole
        # word and gradually removing letters. The point is to find the longest
        # suffix of the word that we know how to handle.        
        found = Lemma.objects.none()
        while found.count() == 0:
            found = Lemma.objects.filter(word=lookup, language=language).order_by('pos__priority')
            if len(lookup) == 0 and found.count() == 0: return (word, [])
            lookup = lookup[1:]
        
        # The result of this search is a list of rows of the lemma table.
        # Now we need to use them to produce a result.
        entries = list(found)
        lemma_forms = []
        canonical = None
        lemmaword = None
        for entry in entries:
            # These lemma forms are showing up in preference order. Take the
            # first one and call it "canonical". Any result that gives a
            # different lemma will be ignored, so that in the end we only
            # need to return one lemma.
            if canonical is None:
                canonical = entry.lemma
                
                # Apply the ending change to the word.
                removechars = len(entry.word.strip('^'))
                lemmaword = word[0:len(word)-removechars] + entry.lemma.strip('^')
            elif entry.lemma != canonical: continue
            # If this result gives us the correct lemma, output the part of
            # speech and inflection that got us there.
            lemma_forms.append((entry.pos, entry.inflection))
        return lemmaword, lemma_forms

    @classmethod
    def lemma_split(cls, word, language):
        if isinstance(language, basestring):
            language = Language.get(language)
        lemma_word, lemma_forms = Lemma.lemmatize(word, language)
        #if not all_inflections: lemma_forms = lemma_forms[0:1]
        #symbol = '|'.join("%s_%s" % inflect_tuple for inflect_tuple in lemma_forms)
        #return lemmaword, symbol
        pos, inflection = lemma_forms[0]
        inflectstr = cls.get_base_inflect().get((pos, inflection,
        language), '')
        if inflectstr == '+': inflectstr = ''
        return lemma_word, inflectstr

    @staticmethod
    def inflect(lemma, pos, inflection, language):
        if isinstance(language, basestring):
            language = Language.get(language)
        if isinstance(pos, basestring):
            pos = PartOfSpeech.objects.get(symbol=pos)
        if isinstance(inflection, basestring):
            inflection = Inflection.objects.get(symbol=inflection, language=language)
        lookup = '^'+lemma
        found = Lemma.objects.none()
        while found.count() == 0:
            found = Lemma.objects.filter(lemma=lookup, pos=pos,
                                         inflection=inflection,
                                         language=language
                                         ).order_by('pos__priority')
            if len(lookup) == 0 and found.count() == 0: return [lemma]
            lookup = lookup[1:]
        result = []
        for entry in found:
            removechars = len(entry.lemma.strip('^'))
            word = lemma[0:len(lemma)-removechars] + entry.word.strip('^')
            result.append(word)
        return result
    
    
    def __str__(self):
        return "%s <=%s=> %s [%s_%s]" % (self.word, self.language.id,
                                           self.lemma, self.pos, self.inflection)
    
    class Meta:
        db_table = 'lemmas'

    _base_inflect = None
    @staticmethod
    def get_base_inflect():
        if Lemma._base_inflect is None:
            Lemma._base_inflect = dict(
                ((lem.pos, lem.inflection, lem.language), lem.word)
                for lem in Lemma.objects.filter(lemma=''))
        return Lemma._base_inflect
    def _instance_base_inflect(self):
        return self.__class__.get_base_inflect()
    base_inflect = property(_instance_base_inflect)

#Lemma.lemmatizer = Lemmatizer(Lemma)

class Pattern(models.Model):
    "Probably obsolete."
    pattern = models.CharField(max_length=255)
    predtype_id = models.IntegerField() # no dependency on conceptnet.models
    polarity = models.IntegerField()
    sort_order = models.IntegerField()
    language = models.ForeignKey(Language)
    
    class Meta:
        db_table = 'parsing_patterns'

class FunctionWord(models.Model):
    """ a word of particular significance to a parser """
    language = models.ForeignKey(Language)
    word = models.TextField()
    unique_together = (('language', 'word'),)

    def __unicode__(self):
        return "<" + self.language.id + ":" + self.word + ">"

    class Meta:
        db_table = 'functionwords'

class FunctionFamily(models.Model):
    """ defines a family of function words """
    family = models.TextField()
    f_word = models.ForeignKey(FunctionWord)
    unique_together = (('family', 'f_word'),)

    def __unicode__(self):
        return self.family + ": " + unicode(self.f_word)

    class Meta:
        db_table = 'functionfamilies'

    @staticmethod
    def build_function_detector(language, family):
        # Prepare the kb
        words = list(FunctionFamily.objects.filter(family=family,f_word__language=language).values_list('f_word__word', flat=True))

        return FunctionFamilyDetector(words,language,family)

class FunctionClass(models.Model):
    """A class of function words. Supersedes the old "FunctionFamily"."""
    name = models.TextField(unique=True)
    words = models.ManyToManyField(FunctionWord)

    def __unicode__(self):
        return u"<FunctionClass: %s>" % self.name

    class Meta:
        db_table = 'functionclass'
        
    def function_word_set(self, language):
        words = self.words.filter(language=language).values_list('word', flat=True)
        return set(words)

