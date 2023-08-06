class DefaultNL(object):
    def is_stopword(self): return False
    def stem_word(self, stuff): return stuff
    def normalize(self, stuff): return stuff

