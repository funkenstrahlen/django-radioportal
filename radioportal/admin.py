'''
Created on 21.05.2011

@author: robert
'''

from radioportal import models
from django.contrib import admin

from guardian.admin import GuardedModelAdmin

class InlineStream(admin.TabularInline):
    model = models.Stream


class StreamSetupAdmin(GuardedModelAdmin):
    inlines = [
        InlineStream,
    ]


class InlineEpisodePart(admin.TabularInline):
    model = models.EpisodePart


class InlineGraphic(admin.TabularInline):
    model = models.Graphic


class InlineRecording(admin.TabularInline):
    model = models.Recording


class EpisodeAdmin(admin.ModelAdmin):
    inlines = [
        InlineEpisodePart,
#        InlineGraphic,
#        InlineRecording,
    ]

class ShowAdmin(GuardedModelAdmin):
    pass

admin.site.register(models.Show, ShowAdmin)
admin.site.register(models.Episode, EpisodeAdmin)
admin.site.register(models.StreamSetup, StreamSetupAdmin)
admin.site.register(models.Status)
