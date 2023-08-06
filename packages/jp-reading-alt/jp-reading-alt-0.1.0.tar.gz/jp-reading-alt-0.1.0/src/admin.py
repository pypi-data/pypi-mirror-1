# -*- coding: utf-8 -*-
#
#  admin.py
#  jp-reading-alt
# 
#  Created by Lars Yencken on 10-04-2009.
#  Copyright 2009 Lars Yencken. All rights reserved.
#

from django.contrib import admin

import models

class KanjiReadingAdmin(admin.ModelAdmin):
    list_display = ('kanji', 'reading', 'alternations')
    list_filter = ('alternations',)

admin.site.register(models.KanjiReading, KanjiReadingAdmin)

class ReadingAlternationAdmin(admin.ModelAdmin):
    list_display = ('value', 'code', 'probability')

admin.site.register(models.ReadingAlternation, ReadingAlternationAdmin)

# vim: ts=4 sw=4 sts=4 et tw=78:

