from models import FunctionWord, FunctionFamily
from csamoa.corpus.models import AutoreplaceRule
import re,random,exceptions


class Chunker_en:
    def __init__(self,language):
             # FIXME: Fail elegantly on other languages
        if not language.id == 'en':
            assert False, "I only know English! " + str(language)

             # Load language utilities
        self.language = language
        from montylingua import MontyLingua
        self.ml = MontyLingua.MontyLingua()
        self.being_words = FunctionFamily.objects.filter(f_word__language=language,family='being')
        self.being_words = [word.word for word in self.being_words]
        self.swaplist = AutoreplaceRule.build_autoreplacer(language,'swaplist')
        self.re_grammar = {
                'IsA':['^ NX $','^ NX (PX )*$'],
                'default':['^ (VX )*(AX )*(NX )*(PX )*$','^ (VX )*(AX )*(NX )*(PX )*$'],
        }
        self.lookup = {}

    def chunk(self,text):
        tagged = self.tag(text)
        return self.ml.chunk_tagged(tagged)

    def tag(self,text):
        toks = self.ml.tokenize(text)
        return self.ml.tag_tokenized(toks)

    def lemmatise(self,text):
        tagged = self.tag(text)
        return self.ml.lemmatise_tagged(tagged)

    def arg_grammar_accept_p(self,arg_chunked,re_pattern):
        toks = arg_chunked.split()
        toks = [('/' in tok and tok or ('/' + tok)) for tok in toks]
        pairs = [tok.split('/') for tok in toks]
        words = [wp[0] for wp in pairs]
        tags = [wp[1] for wp in pairs]

        processed_tags_str = ' '+' '.join(tags)+' '
        collapse_re = " \((.X) .+? (.X)\) "
        collapse_re = re.compile(collapse_re)
        dirtyBit = 1
        while dirtyBit:
            dirtyBit = 0
            m = collapse_re.search(processed_tags_str)
            if m:
                dirtyBit = 1
                chunk_type = m.groups()[0]
                processed_tags_str = processed_tags_str[:m.start()]+' '+chunk_type+' '+processed_tags_str[m.end():]
        arg_pattern = ' '+' '.join(processed_tags_str.split())+' '
        m = re.search(re_pattern,arg_pattern)
        return bool(m)

    def postchunk_px(self,chunked):
        toks = chunked.split()
        toks = [('/' in tok and tok or ('/' + tok)) for tok in toks]
        pairs = [tok.split('/') for tok in toks]
        words = [wp[0] for wp in pairs]
        tags = [wp[1] for wp in pairs]

        pc_re = " (IN )?IN \(NX(.+?) NX\) "
        pc_re = re.compile(pc_re)
        dirtyBit = 1
        while dirtyBit:
            dirtyBit = 0
            processed_tags_str = ' '+' '.join(tags)+' '
            m = pc_re.search(processed_tags_str)
            if m:
                dirtyBit = 1
                how_many_toks_on_the_left = len(processed_tags_str[:m.start()].split())
                how_many_toks_on_the_right = len(processed_tags_str[m.end():].split())
                toks_range = (how_many_toks_on_the_left,len(tags)-how_many_toks_on_the_right)
                chunk_words = words[toks_range[0]:toks_range[1]]
                chunk_tags = tags[toks_range[0]:toks_range[1]]
                chunk = ' '.join([chunk_words[x]+'/'+chunk_tags[x] for x in range(len(chunk_words))])
                nonce = 'PC_'+str(random.randint(0,1000000000))
                cleaned_chunk = ' '.join([x for x in chunk.split() if x not in ['/(NX','/NX)']])
                self.lookup[nonce] = cleaned_chunk
                for i in range(len(words)):
                    if i in range(toks_range[0],toks_range[1]):
                        words[i] = 'bar'
                        tags[i] = nonce
        chunked = ' '.join([words[x]+'/'+tags[x] for x in  range(len(words))])
        chunked_toks = chunked.split()
        output_str = ''
        seen_nounces = []
        for tok in chunked_toks:
            word,pos = tok.split('/')
            if pos in seen_nounces:
                continue
            elif len(pos)>=4 and pos[:len('PC_')] in ['PC_']:
                seen_nounces.append(pos)
                chunk_type = pos[:len('P')]+'X'
                output_str+=' ('+chunk_type+' '+self.lookup.get(pos,'')+' '+chunk_type+') '
            else:
                output_str+=' '+tok+ ' '
        output_str = output_str.replace(' /(NX ',' (NX ')
        output_str = output_str.replace(' /NX) ',' NX) ')
        output_str = ' '.join(output_str.split())
        return output_str

    def chunk_with_px(self,text,re_pattern):
        arg_chunked = self.postchunk_px(self.chunk(text))
        if not self.arg_grammar_accept_p(arg_chunked,re_pattern):
            return False
        return arg_chunked

    def generalize_chunk(self, text, trim_ok=True):
        print "   ... generalizing: ", text
        chunked = self.postchunk_px(self.chunk(text))
        toks = chunked.split()
        toks = [('/' in tok and tok or ('/' + tok)) for tok in toks]
        print "   ... toks: ", ' '.join(toks)
        pairs = [tok.split('/') for tok in toks]
        words = [wp[0] for wp in pairs]
        tags = [wp[1] for wp in pairs]

             # Identify phrase starts and ends
        starts = [('(' in tag) for tag in tags]
        ends = [(')' in tag) for tag in tags]

             # Identify the first phrase
        try:
            i = starts.index(True)
            j = ends.index(True) + 1
        except exceptions.ValueError:
            return []

        if i > 0 or j < len(tags):
            return ' '.join(words[i:j])

             # Abort if adjective trimming is not ok
        if not trim_ok: return text

             # Pull out adjectives and attached adverbs
        if 'JJ' in tags:
            i = tags.index('JJ')
            j = i + 1
            while i > 0 and tags[i-1] == 'RB': i -= 1
            words[i:j] = []
            return ' '.join(words)

             # Operation Complete!
        return text

    def clean(self, text):
        return text.strip(' ').strip('.').strip('?').strip('!')

    def concatenate_be(self, subj, gen_text):
        print "   ... concatenating '" + subj + "' and '" + gen_text + "'"
        return subj + ' is ' + gen_text

    def normalize(self, text,re_pattern_key='default',position=0):
        stop_pos = ['DT','MD',',','.']
        if text[-1] == '.': text = text[0:-1]
        if not self.re_grammar.has_key(re_pattern_key):
            re_pattern_key = 'default'
        re_pattern = self.re_grammar[re_pattern_key][position]

        chunked = self.chunk_with_px(text,re_pattern)
        if not chunked: return None
        toks = chunked.split()

        toks = [('/' in tok and tok or ('/' + tok)) for tok in toks]
        word_pos = [tok.split('/') for tok in toks]
        word_pos = [wp for wp in word_pos if wp[1] not in stop_pos]
        word_pos = [wp for wp in word_pos if not (wp[1] == 'RB' and wp[0].lower() != 'not') ]
        words = [wp[0] for wp in word_pos]
        pos = [wp[1] for wp in word_pos]

        normalized = ' '.join(words)
        normalized = self.swaplist(normalized)

        return normalized
    def constrain_type(self, text, chunktype):
        chunked = self.chunk(text)
        toks = chunked.split()
        if chunktype in ['AX','NX']:
            return (len(toks) > 2 and toks[0] == '(' + chunktype and toks[-1] == chunktype + ')')
        elif chunktype in ['VP', 'VP_noncopula', 'VP_copula']:
            if len(toks) > 2 and toks[0] == '(VX' and toks[-1] in ['VX)','NX)']:
                if chunktype == 'VP': return True
                elif chunktype == 'VP_noncopula':
                    return (len(toks[1].split('/')) == 2 and toks[1].split('/')[0].lower() not in self.being_words)
                elif chunktype == 'VP_copula':
                    return (len(toks[1].split('/')) == 2 and toks[1].split('/')[0].lower() in self.being_words)
        return False

    def constrain_pos(self, text, chunkpos):
        tagged = self.tag(text)
        tags = ' '.join([ x.split('/')[1] for x in tagged.split() ])
        pos_re = re.compile(chunkpos)
        m = pos_re.search(tags)
        return bool(m)

class Chunker_pt:
    def chunk(self,text): return ''
    def constrain_type(self, text, chunktype): assert False, 'Portuguese constrain_type not implemented'
    def constrain_pos(self, text, chunkpos): assert False, 'Portuguese constrain_pos not implemented'
    def clean(self,text): return text
    def generalize_chunk(self, text, trim_ok=True): return text

def GetChunker(language):
    if language.id == 'en': return Chunker_en(language)
    if language.id == 'pt': return Chunker_pt()
    assert False, str(language) + ' has no available chunker'
