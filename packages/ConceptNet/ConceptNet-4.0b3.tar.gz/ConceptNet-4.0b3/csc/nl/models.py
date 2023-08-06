from django.db import models
from csc.corpus.models import Language

class AutoreplaceRule(models.Model):
    """
    An AutoreplaceRule indicates that one word should be replaced by another.
    These rules are used to correct misspellings when parsing ConceptNet.
    """
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

    class Meta:
        db_table = 'corpus_autoreplacerule'
        
    class Admin:
        pass

class FunctionWord(models.Model):
    """
    A FunctionWord is a word that should be handled specially by a parser or
    normalizer. FunctionWords can be grouped into different *classes*
    depending on how they should be handled.

    The most pertinent family of FunctionWord is *stop words*, words that
    should be ignored when normalizing a phrase of text.
    """
    language = models.ForeignKey(Language)
    word = models.TextField()
    unique_together = (('language', 'word'),)

    def __unicode__(self):
        return "<" + self.language.id + ":" + self.word + ">"

    class Meta:
        db_table = 'functionwords'

class FunctionClass(models.Model):
    """A class of function words."""
    name = models.TextField(unique=True)
    words = models.ManyToManyField(FunctionWord)

    def __unicode__(self):
        return u"<FunctionClass: %s>" % self.name

    class Meta:
        db_table = 'functionclass'
        
    def function_word_set(self, language):
        "Get a set of all the words in this class."
        words = self.words.filter(language=language).values_list('word', flat=True)
        return set(words)

