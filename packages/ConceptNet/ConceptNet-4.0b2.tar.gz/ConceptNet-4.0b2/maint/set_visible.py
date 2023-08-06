from csc.util import queryset_foreach
from conceptnet4.models import Concept, Language

en = Language.get('en')
def check_useful(concept):
    if en.nl.is_blacklisted(concept.text):
        concept.visible=False
        concept.save()
        
queryset_foreach(Concept.objects.filter(language=en), check_useful)