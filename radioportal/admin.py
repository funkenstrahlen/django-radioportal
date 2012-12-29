# -*- encoding: utf-8 -*-
# 
# Copyright © 2012 Robert Weidlich. All Rights Reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
# 
# 1. Redistributions of source code must retain the above copyright notice, this
# list of conditions and the following disclaimer.
# 
# 2. Redistributions in binary form must reproduce the above copyright notice,
# this list of conditions and the following disclaimer in the documentation
# and/or other materials provided with the distribution.
# 
# 3. The name of the author may not be used to endorse or promote products
# derived from this software without specific prior written permission.
# 
# THIS SOFTWARE IS PROVIDED BY THE LICENSOR "AS IS" AND ANY EXPRESS OR IMPLIED
# WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO
# EVENT SHALL THE AUTHOR BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT
# OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING
# IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY
# OF SUCH DAMAGE.
# 
'''
Created on 21.05.2011

@author: robert
'''

from radioportal import models
from django.contrib import admin

from guardian.admin import GuardedModelAdmin

class InlineStream(admin.TabularInline):
    model = models.Stream


class ChannelAdmin(GuardedModelAdmin):
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
admin.site.register(models.Channel, ChannelAdmin)
admin.site.register(models.Status)
