from django.contrib.auth.models import User
from csamoa.corpus.models import AutoreplaceRule, Sentence
from csamoa.representation.parsing.models import Batch, Frame, RawPredicate
from csamoa.representation.parsing.tools.models import SecondOrderPattern, FunctionFamily
from csamoa.representation.parsing.tools.processes import GetChunker
from csamoa.representation.presentation.models import Predicate, PredicateType, Stem, RatingValue, Rating
from django.core.paginator import Paginator
from django.db import transaction
from Stemmer import Stemmer
import sys,traceback,string,re

class Processor:
    def __init__(self):
        self.autocorrect = {}
        self.second_order = {}
        self.patterns = {}
        self.chunkers = {}
        self.stemmers = {}
        self.pos_rating_value = RatingValue.objects.get(label='Generally true')
        self.neg_rating_value = RatingValue.objects.get(label='Correct (should be negative)')
        self.pos_rate_down = RatingValue.objects.get(label='Not true')
        self.neg_rate_down = RatingValue.objects.get(label='Incorrect (should be positive)')
        self.stop_words = { 'blacklist': {}, 'graylist': {}, 'stoplist': {} }

    def process_sentence(self,batch,sentence):
        """ extract Frames and RawPredicates from a Sentence """

        lang = sentence.language
        preds = []

         # Make sure the autocorrector is available
        if not self.autocorrect.has_key(lang.id):
            self.autocorrect[lang.id] = AutoreplaceRule.build_autoreplacer(lang, 'autocorrect')

         # Make sure the second order patterns are available
        if not self.second_order.has_key(lang.id):
            self.second_order[lang.id] = SecondOrderPattern.build_splitter(lang)

         # Autocorrect the sentence
        text = self.autocorrect[lang.id](sentence.text)

         # Split the sentence into semantically important parts
        parts = self.second_order[lang.id](text)

         # Process each part
        for part in parts:
            preds += self.process_sentence_part(batch,lang,sentence,part)

         # Operation Complete!
        return preds

    def process_sentence_part(self,batch,language,sentence,text,depth=0):
         # Make sure the applicable patterns are available
        if not self.patterns.has_key(language.id):
            self.patterns[language.id] = language.pattern_set.all()

         # Make sure the applicable chunker is available
        if not self.chunkers.has_key(language.id):
            self.chunkers[language.id] = GetChunker(language)

         # Clean up sentence
        text = self.chunkers[language.id].clean(text)

         # Attempt to parse the sentence
        print "Processing: " + text
        for pattern in self.patterns[language.id]:
            m = pattern(text)

             # Enforce chunk restrictions
            if m:
                     # Extract predicate chunks
                x = m.groups()[pattern.x_loc]
                y = m.groups()[pattern.y_loc]
                if not bool(x) or not bool(y): continue

                     # Restrict chunk types
                if pattern.x_chunktype:
                    xcr = self.chunkers[language.id].constrain_type(x, pattern.x_chunktype)
                    if not xcr: continue

                if pattern.y_chunktype:
                    ycr = self.chunkers[language.id].constrain_type(y, pattern.y_chunktype)
                    if not ycr: continue

                     # Restrict chunk parts of speech
                if pattern.x_pos:
                    xpc = self.chunkers[language.id].constrain_pos(x, pattern.x_pos)
                    if not xpc: continue

                if pattern.y_pos:
                    ypc = self.chunkers[language.id].constrain_pos(y, pattern.y_pos)
                    if not ypc: continue

                     # Extract frame
                frame = self.get_frame( pattern, text, x, y )

                     # Generate predicate
                pred = RawPredicate(
                                batch=batch,
                                language=language,
                                sentence=sentence,
                                frame=frame,
                                predtype=pattern.predtype,
                                text1=x,
                                text2=y,
                                polarity=pattern.polarity,
                                modality=5,
                                depth=depth
                        )
                pred.save()

                     # Operation Complete!
                print "   ... ", str(pred)
                return [pred] #+ self.raw_predicate_recurse(batch,pred,depth)

         # FIXME: Make ConceptuallyRelated out of link grammers
        return []

    def raw_predicate_recurse(self, batch, pred, depth=0):
         # Abort if predicate type does not generalize
        if pred.predtype.generalize_on == 0: return []
        if pred.polarity == -1: return []

         # Increment depth
        depth += 1

         # Load chunker
        chunker = self.chunkers[pred.language.id]

         # Select text
        if pred.predtype.generalize_on == 1:
             # Load arguments
            text = pred.text1
            subj = pred.text2

             # Generalize chunk
            gen_text = chunker.generalize_chunk(text)
            new_text_1 = pred.frame(gen_text, subj)
        else:
            text = pred.text2
            subj = pred.text1

             # Generalize chunk
            gen_text = chunker.generalize_chunk(text)
            new_text_1 = pred.frame(subj, gen_text)

        if not gen_text or gen_text == text: return []

         # Operation Complete!
        return self.process_sentence_part(batch,pred.language,pred.sentence,new_text_1,depth)

    def normalize(self, text, language):
        if not isinstance(text, unicode): text = text.decode('utf-8')
        punct = string.punctuation.replace("'", "")

         # Make sure the applicable stemmer is available
        if not self.stemmers.has_key(language.id):
            self.stemmers[language.id] = Stemmer(language.id)
        stemmer = self.stemmers[language.id]

         # Make sure stop word detector is available
        if not self.stop_words['stoplist'].has_key( language.id ):
            self.stop_words['stoplist'][language.id] = FunctionFamily.build_function_detector( language, 'stop')
        stoplist = self.stop_words['stoplist'][language.id]

         # Normalize text
        words = text.replace('/', ' ').replace('-', ' ').split()
        words = [w.strip(punct).lower() for w in words]
        words = [w for w in words if not stoplist(w)]
        words = [stemmer.stemWord(w) for w in words]
        words.sort()
        return " ".join(words)

    def process_raw_predicate(self,batch,raw_predicate):
        language = raw_predicate.language
        print "Processing:",str(raw_predicate)

         # Normalize text
        stem1 = self.normalize(raw_predicate.text1, language)
         #print "  stem1:", stem1
        stem2 = self.normalize(raw_predicate.text2, language)
         #print "  stem2:", stem2
        if not stem1 or not stem2: return None

         # Find stems
        stem1, created = Stem.objects.get_or_create(text=stem1,language=language)
        if created:
            stem1.words = len(stem1.text.split())
            stem1.save()
        stem2, created = Stem.objects.get_or_create(text=stem2,language=language)
        if created:
            stem2.words = len(stem2.text.split())
            stem2.save()
        print "  ...stems found"

         # Find old predicate, if it exists
        defaults = { 'batch': batch,
                     'raw': raw_predicate,
                     'frame': raw_predicate.frame,
                     'polarity': raw_predicate.polarity,
                     'modality': raw_predicate.modality,
                     'score': 1,
                     'depth': raw_predicate.depth,
                     'language': raw_predicate.language,
                     'visible': True }
        pred, created = Predicate.objects.get_or_create(predtype=raw_predicate.predtype, stem1=stem1, stem2=stem2, defaults=defaults)
        if not created:
            pred.score += 1
            pred.depth = min( pred.depth, raw_predicate.depth )
        else:
            stem1.num_predicates += 1
            stem2.num_predicates += 1
            stem1.save()
            stem2.save()
         # Insert compatibility members
        pred.text1 = raw_predicate.text1
        pred.text2 = raw_predicate.text2
        pred.creator = raw_predicate.sentence.creator
        pred.sentence = raw_predicate.sentence
        pred.save()

         # Create rating
        if pred.polarity == 1: rvs = [self.pos_rating_value, self.pos_rate_down]
        else: rvs = [self.neg_rating_value, self.neg_rate_down]
        if pred.polarity == raw_predicate.polarity: rv = rvs[0]
        else: rv = rvs[1]
        try:
            creator_id = raw_predicate.sentence.creator.id
        except:
            creator_id = User.objects.get(username='dev').id
        rating = pred.rating_set.create(user_id=creator_id,rating_value=rv)

        # Operation Complete!
         #print "  ...result:", str(pred)
        return [pred]

    def get_frame_ex(self,pattern,lang,predtype,mod_text):
              # Attempt to locate existing frame
        old_frame = lang.frame_set.filter(text=mod_text,predtype=predtype)
        if old_frame.count() > 0: return old_frame[0]

              # Build new frame
        new_frame = lang.frame_set.create(
                        predtype=predtype,
                        text=mod_text,
                        pattern=pattern
                        )

              # Operation Complete!
        return new_frame

    def get_frame(self,pattern,text,x,y):
              # Build frame text
        mod_text = text.replace(x, '{1}', 1).replace(y, '{2}', 1) + "."

              # Extract parameters for call to get_frame_ex
        lang = pattern.language
        predtype = pattern.predtype

              # Operation Complete!
        return self.get_frame_ex(pattern, lang, predtype, mod_text)


def process_sentence_batch(user,sentences,stem=False,start_page=0):
    """ apply process_sentence to a set of Sentences """

     # Create batch
    batch = Batch()
    batch.owner = user

     # Create processor
    proc = Processor()

     # Create sentence paginator
    paginator = Paginator(sentences,10)
    pages = ((i,paginator.get_page(i)) for i in range(start_page,paginator.pages))

     # Define an internal routine for transaction isolation
    @transaction.commit_on_success
    def do_batch(sentences):
        for sentence in sentences:
            try:
                preds = proc.process_sentence(batch,sentence)
                if stem:
                    for pred in preds:
                        proc.process_raw_predicate(batch,pred)
            except Exception,e:
                # Add sentence
                e.sentence = sentence

                # Extract traceback
                e_type, e_value, e_tb = sys.exc_info()
                e.tb = "\n".join(traceback.format_exception( e_type, e_value, e_tb ))

                # Raise again
                raise e

     # Process sentences
    for (i,sentences) in pages:
        # Update progress
        batch.status = "process_sentence_batch " + str(i) + "/" + str(paginator.pages)
        batch.progress_num = i
        batch.progress_den = paginator.pages
        batch.save()

        try: do_batch(sentences)
        except Exception, e:
            batch.status = "process_sentence_batch " + str(i) + "/" + str(paginator.pages) + " ERROR!"
            batch.remarks = str(e.sentence) + "\n" + str(e) + "\n" + e.tb
            print "****TRACEBACK***"
            print batch.remarks
            batch.save()
            raise e

     # Report completion
    batch.status = "process_sentence_batch " + str(paginator.pages) + "/" + str(paginator.pages) + " DONE"
    batch.progress_num = batch.progress_den
    batch.save()

def process_brill_batch(user,skip_lines=0):
    """ load a set of raw predicates from the Brill engine """

     # Create batch
    batch = Batch()
    batch.owner = user
    batch.save()

     # Create a processor
    proc = Processor()

     # Define a RawPredicate generator
    def raw_predicate_generator(batch,pre_generator):
        for (sentence_id, predtype_id, polarity, text1, text2, frame_text) in pre_generator:
            sent = Sentence.objects.get(id=sentence_id)
            predtype = PredicateType.objects.get(id=predtype_id)
            lang = sent.language
            frame = proc.get_frame_ex(None, lang, predtype, frame_text)

            pred = RawPredicate(
                            batch=batch,
                            language=lang,
                            sentence=sent,
                            frame=frame,
                            predtype=predtype,
                            text1=text1,
                            text2=text2,
                            polarity=polarity,
                            modality=5,
                            depth=0)

            pred.save()
            yield pred

        # Operation Complete!

     # Define a clustering routine
    def cluster(count,gen):
        while True:
            lst = []
            for i in range(count):
                try:
                    lst.append( gen.next() )
                except StopIteration:
                    yield lst
                    return
            yield lst

        # Operation Complete!

     # Define an internal routine for transaction isolation
    @transaction.commit_on_success
    def do_batch(raw_predicates):
        for raw_predicate in raw_predicates:
            try:
                proc.process_raw_predicate(batch,raw_predicate)
            except Exception,e:
                # Add predicate
                e.raw_predicate = raw_predicate

                # Extract traceback
                e_type, e_value, e_tb = sys.exc_info()
                e.tb = "\n".join(traceback.format_exception( e_type, e_value, e_tb ))

                # Raise again
                raise e

     # Process predicates
    from csamoa.representation.parsing.tools.parse import generate_predicates
    i = 0
    print "about to skip", skip_lines, "lines"
    for pred_cluster in cluster(10, raw_predicate_generator( batch, generate_predicates(skip=skip_lines) )):
        # Update progress
        i = i + 1
        batch.status = "process_brill_batch " + str(i)
        batch.progress_num = i
        batch.progress_den = i + 1
        batch.save()

        try: do_batch(pred_cluster)
        except Exception, e:
            batch.status = "process_brill_batch " + str(i) + " ERROR!"
            batch.remarks = str(e.raw_predicate) + "\n" + str(e) + "\n" + e.tb
            print "****TRACEBACK***"
            print batch.remarks
            batch.save()
            raise e

     # Report completion
    batch.status = "process_brill_batch " + str(i) + " DONE"
    batch.progress_num = i
    batch.progress_den = i
    batch.save()

     # Operation Complete!

def process_predicate_batch(user,raw_predicates,start_pred=0):
    """ apply process_sentence to a set of Sentences """

     # Create batch
    batch = Batch()
    batch.owner = user

     # Create processor
    proc = Processor()

     # Create predicate paginator
    paginator = ObjectPaginator(raw_predicates,10)
    pages = ((i,paginator.get_page(i)) for i in range(start_pred,paginator.pages))

     # Define an internal routine for transaction isolation
    @transaction.commit_on_success
    def do_batch(raw_predicates):
        for raw_predicate in raw_predicates:
            try:
                proc.process_raw_predicate(batch,raw_predicate)
            except Exception,e:
                # Add predicate
                e.raw_predicate = raw_predicate

                # Extract traceback
                e_type, e_value, e_tb = sys.exc_info()
                e.tb = "\n".join(traceback.format_exception( e_type, e_value, e_tb ))

                # Raise again
                raise e

     # Process predicates
    for (i,raw_predicates) in pages:
        # Update progress
        batch.status = "process_predicate_batch " + str(i) + "/" + str(paginator.pages)
        batch.progress_num = i
        batch.progress_den = paginator.pages
        batch.save()

        try: do_batch(raw_predicates)
        except Exception, e:
            batch.status = "process_predicate_batch " + str(i) + "/" + str(paginator.pages) + " ERROR!"
            batch.remarks = str(e.raw_predicate) + "\n" + str(e) + "\n" + e.tb
            print "****TRACEBACK***"
            print batch.remarks
            batch.save()
            raise e

     # Report completion
    batch.status = "process_predicate_batch " + str(paginator.pages) + "/" + str(paginator.pages) + " DONE"
    batch.progress_num = batch.progress_den
    batch.save()
