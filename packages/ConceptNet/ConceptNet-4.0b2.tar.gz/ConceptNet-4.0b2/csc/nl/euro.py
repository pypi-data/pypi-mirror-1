import string
from csc.nl import NLTools, get_nl
from csc.corpus.models import Language
from csc.nl.models import FunctionClass, AutoreplaceRule
import re

def doctest_globals():
    en_nl = get_nl('en')
    return locals()

def tokenize(text):
    step0 = text.replace('\r', '').replace('\n', ' ')
    step1 = step0.replace(" '", " ` ").replace("'", " '").replace("n 't", " n't")
    step2 = re.sub('"([^"]*)"', r" `` \1 '' ", step1)
    step3 = re.sub(r'([.,:;?!%]+) ', r" \1 ", step2)
    step4 = re.sub(r'([.,:;?!%]+)$', r" \1", step3)
    step5 = re.sub(r'([()])', r" \1 ", step4)
    return re.sub(r'  +', ' ', step5).strip()

def untokenize(text):
    step1 = text.replace("`` ", '"').replace(" ''", '"')
    step2 = step1.replace(" ( ", " (").replace(" ) ", ") ")
    step3 = re.sub(r' ([.,:;?!%]+)([ \'"`])', r"\1\2", step2)
    step4 = re.sub(r' ([.,:;?!%]+)$', r"\1", step3)
    step5 = step4.replace(" '", "'").replace(" n't", "n't")
    step6 = step5.replace(" ` ", " '")
    return step6.strip()

class EuroNL(NLTools):
    """
    A language that generally follows our assumptions about European languages.
    Only the subclasses of EuroNL -- :class:`StemmedEuroNL` and
    :class:`LemmatizedEuroNL` -- implement all of the NLTools operations.
    """
    # TODO: Refactor this so that stemming languages and lemmatizing languages
    # aren't mixed up.

    def __init__(self, lang):
        # Set up the NLTools object, including loading simple data
        # from the database.
        self.lang = lang
        self.model = Language.get(lang)
        
        # old version
        self.old_stopwords = FunctionClass.objects.get(name='stop_old').function_word_set(lang)
        
        # new version (ConceptNet 3.5 and 4)
        self.stopwords = FunctionClass.objects.get(name='stop').function_word_set(lang)
        self.blacklist = set([x.lower() for x in
        FunctionClass.objects.get(name='blacklist').function_word_set(lang)])
        self.swapdict = {}
        self.autocorrect = {}

        for replacerule in AutoreplaceRule.objects.filter(language=lang,
        family='swap4'):
            self.swapdict[replacerule.match] = replacerule.replace_with
        for replacerule in AutoreplaceRule.objects.filter(language=lang,
        family='autocorrect'):
            self.autocorrect[replacerule.match] = replacerule.replace_with
        
    def is_stopword(self, word):
        """
        A *stopword* is a word that contributes little to the semantic meaning
        of a text and should be ignored. These tend to be short, common words
        such as "of", "the", and "you".
        
        Stopwords are often members of closed classes such as articles and
        prepositions.

        Whether a word is a stopword or not is a judgement call that depends on
        the application. In ConceptNet, we began with the stock lists of
        stopwords from NLTK, but we have refined and tweaked the lists
        (especially in English) over the years.

        Examples::

            >>> en_nl = get_nl('en')
            >>> en_nl.is_stopword('the')
            True
            >>> en_nl.is_stopword('defenestrate')
            False

            >>> pt_nl = get_nl('pt')      # This time, in Portuguese
            >>> pt_nl.is_stopword('os')
            True
            >>> pt_nl.is_stopword('the')
            False
        """
        return word in self.stopwords

    def is_blacklisted(self, text):
        """
        The blacklist is used to discover and discard particularly unhelpful
        phrases.

        A phrase is considered "blacklisted" if *every* word in it appears on
        the blacklist. The empty string is always blacklisted.

            >>> en_nl.is_blacklisted('x')
            True
            >>> en_nl.is_blacklisted('the')
            False
            >>> en_nl.is_blacklisted('a b c d')
            True
            >>> en_nl.is_blacklisted('a b c d puppies')
            False
        """
        if not isinstance(text, unicode): text = text.decode('utf-8')
        words = self.tokenize(text).split(' ')
        for word in words:
            if word not in self.blacklist: return False
        return True

    def tokenize(self, text):
        r"""
        Tokenizing a sentence inserts spaces in such a way that it separates
        punctuation from words, splits up contractions, and generally does what
        a lot of natural language tools (especially parsers) expect their
        input to do.
        
            >>> en_nl.tokenize("Time is an illusion. Lunchtime doubly so.")
            'Time is an illusion . Lunchtime doubly so .'
            >>> untok = '''
            ... "Very deep," said Arthur, "you should send that in to the
            ... Reader's Digest. They've got a page for people like you."
            ... '''
            >>> tok = en_nl.tokenize(untok)
            >>> tok
            "`` Very deep , '' said Arthur , `` you should send that in to the Reader 's Digest . They 've got a page for people like you . ''"
            >>> en_nl.untokenize(tok)
            '"Very deep," said Arthur, "you should send that in to the Reader\'s Digest. They\'ve got a page for people like you."'
            >>> en_nl.untokenize(tok) == untok.replace('\n', ' ').strip()
            True

        """
        return tokenize(text)

    def untokenize(self, text):
        """
        Untokenizing a text undoes the tokenizing operation, restoring
        punctuation and spaces to the places that people expect them to be.

        Ideally, `untokenize(tokenize(text))` should be identical to `text`,
        except for line breaks.
        """
        return untokenize(text)

class LemmatizedEuroNL(EuroNL):
    @property
    def lemmatizer(self):
        """
        The `.lemmatizer` property lazily loads an MBLEM lemmatizer from the
        disk. The resulting object is an instance of
        :class:`csc.nl.mblem.trie.Trie`.
        """
        if not hasattr(self, '_lemmatizer'):
            from csc.nl.mblem import get_mblem
            self._lemmatizer = get_mblem(self.lang)
        return self._lemmatizer

    @property
    def unlemmatizer(self):
        """
        The `.unlemmatizer` property lazily loads an MBLEM unlemmatizer from
        the disk. The resulting object is a dictionary of tries, one for each
        possible combination of part-of-speech and inflection that can be
        added.
        """
        if not hasattr(self, '_unlemmatizer'):
            from csc.nl.mblem import get_unlem
            self._unlemmatizer = get_unlem(self.lang)
        return self._unlemmatizer

    def word_split(self, word):
        """
        Divide a single word into a string representing its *lemma form* (its
        base form without inflections), and a second string representing the
        inflections that were removed.

        Instead of abstract symbols for the inflection, we currently represent
        inflections as their most common natural language string. For example,
        the inflection string 's' represents both "plural" and "third-person
        singular".

        This odd representation basically makes the assumption that, when two
        inflections look the same, they will act the same on any word. Thus, we
        can avoid trying to disambiguate different inflections when they will
        never make a difference. (There are cases where this is not technically
        correct, such as "leafs/leaves" in "there were leaves on the ground"
        versus "he leafs through the pages", but we don't lose sleep over it.)

        >>> en_nl.word_split(u'lemmatizing')
        (u'lemmatize', u'ing')
        >>> en_nl.word_split(u'cow')
        (u'cow', u'')
        >>> en_nl.word_split(u'went')
        (u'go', u'ed')
        """
        try:
            lemma, pos, infl = self.lemmatizer.mblem(word)[0]
            residue = self.unlemmatizer[pos, infl].leaves()[0].add
            return (lemma, residue)
        except IndexError:
            return (word, u'')
        
    def lemma_split(self, text, keep_stopwords=False):
        """
        When you *lemma split* or *lemma factor* a string, you get two strings
        back:

        1. The *normal form*, a string containing all the lemmas of the
           non-stopwords in the string.
        2. The *residue*, a string containing all the stopwords and the
           inflections that were removed.

        These two strings can be recombined with :meth:`lemma_combine`.

            >>> en_nl.lemma_split("This is the testiest test that ever was tested")
            (u'testy test ever test', u'this is the 1iest 2 that 3 was 4ed')
        """
        if not isinstance(text, unicode): text = text.decode('utf-8')
        text = self.tokenize(text)
        punct = string.punctuation.replace("'", "").replace('-',
        '').replace("`", "")
        
        words = text.replace('/', ' ').split()
        words = [w.strip(punct).lower() for w in words]
        words = [self.autocorrect.get(word, word) for word in words if word]
        lemma_tuples = [self.word_split(word) for word in words]
        lemmas_pre = []
        residue_pre = []
        lemma_index = 0
        for i in range(len(words)):
            if not keep_stopwords and words[i] in self.stopwords:
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
        for lemma_index, ltext in residue_pre:
            if lemma_index is None: residue.append(ltext)
            else: residue.append(str(invpermute[lemma_index]+1) + ltext)
        if len(lemmas) == 0 and not keep_stopwords:
            return self.lemma_split(text, keep_stopwords=True)
        return (u' '.join(lemmas), u' '.join(residue))
    lemma_factor = lemma_split

    def normalize(self, text):
        """
        When you *normalize* a string (no relation to the operation of
        normalizing a vector), you remove its stopwords and infl9ections so that
        it becomes equivalent to similar strings.

        Normalizing involves running :meth:`lemma_split` and keeping only the
        first factor, thus discarding the information that would be used to
        reconstruct the full string.

            >>> en_nl.normalize("this is the testiest test that ever was tested")
            u'testy test ever test'
        """
        return self.lemma_split(text)[0]
    normalize4 = normalize

    def lemma_combine(self, lemmas, residue):
        """
        This is the inverse of :meth:`lemma_factor` -- it takes in a normal
        form and a residue, and re-assembles them into a phrase that is
        hopefully comprehensible.

            >>> en_nl.lemma_combine(u'testy test ever test',
            ... u'this is the 1iest 2 that 3 was 4ed')
            u'this is the testiest test that ever was tested'
        """
        words = []
        lemmas = lemmas.split(' ')
        for res in residue.split(' '):
            if res and res[0] in '0123456789':
                numstr, pos, infl = self.lemmatizer.mblem(res)[0]
                while numstr[-1] not in '0123456789': numstr = numstr[:-1]
                num = int(numstr)
                inflected = self.unlemmatizer[pos, infl].unlem(lemmas[num-1])[0]
                words.append(inflected)
            else:
                words.append(res)
        return self.untokenize(' '.join(words))

class StemmedEuroNL(EuroNL):
    @property
    def stemmer(self):
        if not hasattr(self, '_stemmer'):
            from Stemmer import Stemmer
            self._stemmer = Stemmer(self.lang)
        return self._stemmer

    def stem_word(self, word):
        return self.stemmer.stemWord(word)

    def word_split(self, word):
        stem = self.stem_word(word)
        residue = word[len(stem):]
        return (stem, residue)
    
    def is_stopword(self, word):
        return word in self.old_stopwords

    def normalize(self, text):
        if not isinstance(text, unicode): text = text.decode('utf-8')
        punct = string.punctuation.replace("'", "")
        words = text.replace('/', ' ').replace('-', ' ').split()
        words = [w.strip(punct).lower() for w in words]
        words = [w for w in words if not self.is_stopword(w)]
        words = [self.stem_word(w) for w in words]
        words.sort()
        return u" ".join(words)

