from util import register_admin

models = (
    'Language',
    'Activity',
    'Sentence',
    'AutoreplaceRule',
    'FunctionClass')

register_admin('corpus.models', models)

from django.contrib import admin
from corpus.models import PartOfSpeech, Inflection, Lemma, FunctionWord

class FunctionWordAdmin(admin.ModelAdmin):
    ordering = ('language', 'word')

class InflectionAdmin(admin.ModelAdmin):
    list_display = ('symbol', 'description')

class PartOfSpeechAdmin(admin.ModelAdmin):
    list_display = ('symbol', 'priority')
    ordering = ('priority',)

class LemmaAdmin(admin.ModelAdmin):
    list_display = ('word', 'lemma', 'language', 'pos', 'inflection')
    list_filter = ('language', 'pos', 'inflection')

admin.site.register(Inflection, InflectionAdmin)
admin.site.register(PartOfSpeech, PartOfSpeechAdmin)
admin.site.register(Lemma, LemmaAdmin)
admin.site.register(FunctionWord, FunctionWordAdmin)
