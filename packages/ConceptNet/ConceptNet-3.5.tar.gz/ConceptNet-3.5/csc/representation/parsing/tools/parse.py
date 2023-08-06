import re

### BEGIN PREAMBLE ###

import sys, os, pickle, random
# Uncomment and adjust the next line for scripts
# that run outside the parent-of-csamoa path.
# sys.path += ['/path/to/PARENT/of/csamoa/']
#sys.path += ['/home/rspeer/think/']
os.environ['DJANGO_SETTINGS_MODULE'] = 'csamoa.settings'

#import csamoa.manage

from csamoa.representation.parsing.processes import *
from csamoa.representation.parsing.tools.models import *
from django.contrib.auth.models import User
from csamoa.corpus.models import *
from csamoa.representation.presentation.models import *

from collections import defaultdict

processor = Processor()
lang_en = Language.objects.get(id="en")

# End CSamoa

def unbrill(text):
    step1 = re.sub(r' ([.,:;?!()%]) ', r"\1", text)
    step2 = re.sub(r' ([.,:;?!()%])$', r"\1", step1)
    step3 = step2.replace(" `` ", '"').replace(" '' ", '"')
    step4 = step3.replace(" '", "'").replace(" n't", "n't")
    return step4

def ddict(*args):
    return defaultdict(ddict, *args)

rules = [
    ("{N'}", ["NN", "NNS", "NN {N'}"]),
#    ("{Npl}", ["NNS", "NN {Npl}"]),
    ("{Npr}", ["NNP", "NNP {Npr}"]),
    ("{AP}", ["JJ", "VBN", "PRP$", "{AP} {AP}", "{AP} and {AP}",
              "{AP} , {AP}", "{NP} POS", "JJR", "JJS", "CD"]),
    ("{NP}", ["DT {AP} {N'}", "{AP} {N'}", "DT {N'}",
              "{N'}", "{Npr}", "VBG", "PRP", "VBG {NP}", "VBG {NP} RB",
              "VBG {P}", "VBG {NP} {P}", "{NP} {PP}", "{NP} and {NP}"]),
    ("{P}", ["IN", "TO"]),
    ("{PP}", ["{P} {NP}", "TO {VP}"]),
    ("{BE}", ["be", "is", "are", "was", "were", "being", "been", "MD be",
              "MD RB be", "'s", "'re", "'m"]),
    ("{CHANGE}", ["get", "become", "gets", "becomes"]),
    ("{ADVP}", ["", "RB", "RB RB", "MD RB", "{DO} RB"]),
    ("{DO}", ["do", "does", "did"]),
    ("{V}", ["VB", "VBP", "go VB", "go and VB", "VBZ"]),
    ("{VP}", ["{ADVP} {V}", "{ADVP} {V} {NP}", "{ADVP} {V} {PP}",
              "{BE} {NP}", "{BE} {AP}", "{CHANGE} {AP}", "{VP} RB"]),
    ("{TAG}", ["", "VBN {PP}", "WDT {VP}", "WDT {S}"]),
    ("{S}", ["{NP} {VP}"]),
    ("{XP}", ["{NP}", "{VP}", "{S}"]),
    ("{PASV}", ["VBN", "VBN {PP}", "VBN {PP} {PP}"])
]

parserules = []
for chunktype, exprs in rules:
    for expr in exprs:
        parserules.append((chunktype, expr.split()))

#cursor.execute("""
#select * from parsing_patterns where language_id='en' order by sort_order;
#""")

patterns = list(ParsingPattern.objects.filter(language=lang_en).order_by('sort_order'))

def list_tags(sentence):
    sentence = sentence.strip().replace('/', '_')
    return [word.split('_') for word in sentence.split()]

def chunk(tagged_sentence):
    # Dictionary mapping chunk-names to start positions to end positions to
    # True. This representation is implemented by a ddict (a defaultdict of
    # ddicts).
    words = [[word]+tags[:2] for word, tags in tagged_sentence.tagged_words()]

    chunks = ddict()
    changed = True
    while changed:
        changed = False
        for chunktype, expr in parserules:
            for i in range(len(words)+1):
                start = i
                for end, ignore in check_chunk(words, chunks, expr, start, 0):
                    if not chunks[chunktype][start][end]:
                        chunks[chunktype][start][end] = changed = True
                        #print chunktype, words[start:end]
    return chunks

def check_chunk(words, chunks, chunkexpr, startword, startchunk):
    """
    Returns a generator of (position, labels) tuples. 'position' is the
    word index where the match ended, and 'labels' contains the word indices
    that match against labeled subexpressions.
    """
    if startchunk == len(chunkexpr):
        yield startword, {}
        return
    first = chunkexpr[startchunk]
    if len(words) > startword and first.lower() in [x.lower() for x in words[startword]]:
        for result in check_chunk(words, chunks, chunkexpr, startword+1,
        startchunk+1):
            yield result
    if first.startswith('{'):
        if ':' in first:
            before, after = first.split(':', 1)
            label = after[:-1]
            first = before+'}'
        else: label = None
        keys = chunks[first][startword].keys()
        keys.sort()
        for next in keys:
            for endword, labels in check_chunk(words, chunks, chunkexpr, next,
            startchunk+1):
                newlabels = dict(labels)
                newlabels[label] = (startword, next)
                yield (endword, newlabels)

def check_pattern(sentence, chunkstr):
    words = list_tags(sentence)
    chunkexpr = chunkstr.split()
    chunks = chunk(sentence)
    for endword, labels in check_chunk(words, chunks, chunkexpr, 0, 0):
        if endword == len(words):
            return labels

def test_pattern(sentence, chunkstr):
    rawwords = sentence.split()
    labels = check_pattern(sentence, chunkstr)
    if labels is not None:
        start1, end1 = labels['1']
        start2, end2 = labels['2']
        return [" ".join(rawwords[start1:end1]),
                " ".join(rawwords[start2:end2])]

def try_patterns(tagged_sentence):
    twords = list(tagged_sentence.tagged_words())
    sentence = unbrill(' '.join(tw[0] for tw in twords))
    chunks = chunk(tagged_sentence)
    rawwords = [tw[0] for tw in twords]
    words = [[word]+tags[:2] for word, tags in tagged_sentence.tagged_words()]

    
    for word in rawwords:
        if (word in ['this', 'these'] or word.startswith('fuck') or
        word.startswith('bitch') or word.startswith('nigg')):
            return None
    for pattern in patterns:
        chunkexpr = pattern.pattern.split()
        pol = pattern.polarity
        for word in rawwords:
            if word in ['no', 'not', "n't", "rarely", 'never', 'nothing']:
                pol = -pol
        for endword, labels in check_chunk(words, chunks, chunkexpr, 0, 0):
            if endword == len(words):
                start1, end1 = labels['1']
                start2, end2 = labels['2']
                text1 = unbrill(' '.join(rawwords[start1:end1]))
                text2 = unbrill(' '.join(rawwords[start2:end2]))
                raw3 = list(rawwords)
                if start1 > start2:
                    raw3[start1:end1] = ['{1}']
                    raw3[start2:end2] = ['{2}']
                else:
                    raw3[start2:end2] = ['{2}']
                    raw3[start1:end1] = ['{1}']
                text3 = unbrill(' '.join(raw3))
                return [pattern.predtype.id, pol, text1, text2, text3]

def generate_predicates():
    # [[sentence_id, predtype_id, polarity, text1, text2, frame_text] ... ]
    for ts in TaggedSentence.objects.all():
        yield try_patterns(ts)

def main():
    for result in generate_predicates(): print result

if __name__ == '__main__': main()

# vim:tw=0:
