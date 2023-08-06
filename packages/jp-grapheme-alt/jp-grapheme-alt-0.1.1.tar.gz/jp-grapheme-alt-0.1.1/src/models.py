# -*- coding: utf-8 -*-
# 
#  models.py
#  jp-grapheme-alt
#  
#  Created by Lars Yencken on 2009-04-20.
#  Copyright 2009 Lars Yencken. All rights reserved.
# 

import math

from django.db import models
from django.conf import settings

ALTERNATION_TYPES = (
        ('/', 'root node'),
        ('k', 'kanji node'),
        ('b', 'base reading'),
        ('v', 'vowel length'),
        ('s', 'sequential voicing'),
        ('g', 'sound euphony'),
        ('p', 'palatalization'),
        ('G', 'graphical similarity'),
        ('S', 'semantic similarity'),
        ('c', 'cooccurrence'),
    )

class GraphemeAlternation(models.Model):
    "The probability of the base_form given the surface_form."
    surface_form = models.CharField(max_length=settings.UTF8_BYTES_PER_CHAR,
            db_index=True,
            help_text='The observed form of the grapheme.')

    base_form = models.CharField(max_length=settings.UTF8_BYTES_PER_CHAR,
            db_index=True,
            help_text='The underlying form from which the surface is derived.')

    code = models.CharField(max_length=1, choices=ALTERNATION_TYPES,
            help_text='The type of alternation which occurred.')

    # The probability P(base_form|surface_form), approximated by
    # P(surface_form|base_form)P(base_form).
    probability = models.FloatField(
            help_text='An approximation of P(base_form|surface_form).')

    def __unicode__(self):
        return 'P(%s|%s) = %g' % (
                self.base_form,
                self.surface_form,
                math.exp(self.probability),
            )
