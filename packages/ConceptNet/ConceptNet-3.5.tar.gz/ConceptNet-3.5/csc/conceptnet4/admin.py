from util import register_admin

# Un-customized models
models = (
    'Batch',
    'RawAssertion',
    'Concept',
    'Assertion',
    )
register_admin('conceptnet4.models', models)

# Custom admin
from django.contrib import admin
from conceptnet4.models import Frequency, Frame

class FrequencyAdmin(admin.ModelAdmin):
    list_display = ('language', 'text', 'value')
    list_filter = ('language',)
admin.site.register(Frequency, FrequencyAdmin)

class FrameAdmin(admin.ModelAdmin):
    list_display = ('id', 'language','relation','text','preferred')
    list_filter = ('language','relation')
    list_per_page = 100
    fields = ('relation', 'text', 'language', 'goodness', 'frequency')
admin.site.register(Frame, FrameAdmin)
