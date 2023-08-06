# -*- coding: utf-8 -*-
# 
#  admin.py
#  jp-grapheme-alt
#  
#  Created by Lars Yencken on 2009-04-20.
#  Copyright 2009 Lars Yencken. All rights reserved.
# 

from django.contrib import admin
from django.db.models import get_model

class GraphemeAlternationAdmin(admin.ModelAdmin):
    list_display = ('surface_form', 'base_form', 'code', 'probability')
    list_filter = ('code',)
    search_fields = ('surface_form', 'base_form')

admin.site.register(
        get_model('jp_grapheme_alt', 'graphemealternation'),
        GraphemeAlternationAdmin,
    )