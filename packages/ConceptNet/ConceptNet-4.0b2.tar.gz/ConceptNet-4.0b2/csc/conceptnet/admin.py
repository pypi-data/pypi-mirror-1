from util import register_admin

# Un-customized models
models = (
    'Relation',
    'Batch',
    'RawAssertion',
    'Concept',
    'Assertion',
    'RatingValue',
    'Rating',
#   'Frame',
    )
register_admin('conceptnet.models', models)

# Custom admin
from django.contrib import admin
from conceptnet.models import Frequency, Frame

class FrequencyAdmin(admin.ModelAdmin):
    list_display = ('language', 'text', 'value')
    list_filter = ('language',)
admin.site.register(Frequency, FrequencyAdmin)

class FrameAdmin(admin.ModelAdmin):
    list_display = ('language','relation','text','preferred')
    list_filter = ('language','should_translate','relation')
    list_per_page = 100
    fields = ('relation', 'text', 'language', 'goodness', 'frequency',
              'text_question1', 'text_question2', 'text_question_yn')
#admin.site.register(Frame, FrameAdmin)
