import string

from corpus.models import Language, Lemma, FunctionClass,\
  AutoreplaceRule
#from csamoa.corpus.parse.models import FunctionFamily
import re

def tokenize(text):
    step1 = text.replace("'", " '").replace("n 't", " n't")
    step2 = re.sub('"([^"]*)"', r" `` \1 '' ", step1)
    step3 = re.sub(r'([.,:;?!%]+) ', r" \1 ", step2)
    step4 = re.sub(r'([.,:;?!%]+)$', r" \1", step3)
    step5 = re.sub(r'([()])', r" \1 ", step4)
    return step5.replace("  ", " ")

def untokenize(text):
    step1 = text.replace("`` ", '"').replace(" ''", '"')
    step2 = step1.replace(" ( ", " (").replace(" ) ", ") ")
    step3 = re.sub(r' ([.,:;?!%]+) ', r"\1 ", step2)
    step4 = re.sub(r' ([.,:;?!%]+)$', r"\1", step3)
    step5 = step4.replace(" '", "'").replace(" n't", "n't")
    return step5

class EuroNL(object):
    def __init__(self, lang):
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
        
        self.stems = {}

    @property
    def stemmer(self):
        if not hasattr(self, '_stemmer'):
            from Stemmer import Stemmer
            self._stemmer = Stemmer(self.lang)
        return self._stemmer

    def is_stopword(self, word):
        """
        Deprecated version. Used while we still need to normalize the old way.
        """
        return word in self.old_stopwords

    def stem_word(self, word):
        if word in self.stems:
            return self.stems[word]
        return self.stemmer.stemWord(word)

    def normalize(self, text):
        if not isinstance(text, unicode): text = text.decode('utf-8')
        punct = string.punctuation.replace("'", "")
        words = text.replace('/', ' ').replace('-', ' ').split()
        words = [w.strip(punct).lower() for w in words]
        words = [w for w in words if not self.is_stopword(w)]
        words = [self.stem_word(w) for w in words]
        words.sort()
        return u" ".join(words)

    def is_blacklisted(self, text):
        if not isinstance(text, unicode): text = text.decode('utf-8')
        words = text.split()
        for word in words:
            if word not in self.blacklist: return False
        return True

    def lemma_factor(self, text, keep_stopwords=False):
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

    def normalize4(self, text):
        return self.lemma_factor(text)[0]
    

    def lemma_combine(self, lemmas, residue):
        words = []
        lemmas = lemmas.split(' ')
        for res in residue.split(' '):
            if res and res[0] in '0123456789':
                numstr, lemma_forms = Lemma.lemmatize(res, self.lang)
                num = int(numstr.strip('+'))
                pos, infl = lemma_forms[0]
                inflected = Lemma.inflect(lemmas[num-1], pos, infl, self.lang)[0]
                words.append(inflected)
            else:
                words.append(res)
        print words
        return ' '.join(words)
