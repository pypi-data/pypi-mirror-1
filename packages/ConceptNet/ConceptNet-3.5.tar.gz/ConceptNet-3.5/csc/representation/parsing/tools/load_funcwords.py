#!/usr/bin/env python
from csamoa.representation.parsing.tools.models import FunctionWord, FunctionFamily
from csamoa.corpus.models import Language

import sys

if len(sys.argv) != 3:
    print "Usage: %s language family" % sys.argv[0]
    sys.exit(1)

language = sys.argv[1]
lang = Language.get(language)
family = sys.argv[2]

from django.db import transaction

@transaction.commit_on_success
def go():
    for line in sys.stdin:
        word = line.strip()
        fw = FunctionWord(language=lang, word=word)
        fw.save()
        ff = FunctionFamily(family=family, f_word=fw)
        ff.save()


go()
