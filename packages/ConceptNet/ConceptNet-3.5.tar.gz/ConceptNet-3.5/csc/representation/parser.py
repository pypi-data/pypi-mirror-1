__version__ = "3.0"
__author__ = "havasi@media.mit.edu, rspeer@media.mit.edu, hugo@media.mit.edu, jalonso@media.mit.edu"
__url__ = 'www.conceptnet.org'
# December 5th, 2006 - Catherine Havasi, Rob Speer, Jason Alonso

# FIXME: This file needs to be completed and converted away from montylingua

def chunk(self,text):
    # To be converted
    toked_text = self.theMontyLingua.tokenize(text)
    tagged_text = self.theMontyLingua.tag_tokenized(toked_text)
    chunked = self.theMontyLingua.chunk_tagged(tagged_text)
    return chunked

def tag(self,text):
    # To be converted
    toked_text = self.theMontyLingua.tokenize(text)
    tagged_text = self.theMontyLingua.tag_tokenized(toked_text)
    return tagged_text
