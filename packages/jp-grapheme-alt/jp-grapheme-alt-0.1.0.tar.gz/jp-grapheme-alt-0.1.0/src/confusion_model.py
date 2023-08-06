# -*- coding: utf-8 -*-
# 
#  confusion_model.py
#  jp-grapheme-alt
#  
#  Created by Lars Yencken on 2007-12-29.
#  Copyright 2007-2008 Lars Yencken. All rights reserved.
# 

"Grapheme confusion models based on orthographic or semantic similarity."

#----------------------------------------------------------------------------#

import os
import math

from django.conf import settings
from cjktools.sequences import ithread
from cjktools.common import sopen
from simplestats import freq

#----------------------------------------------------------------------------#

_char_freq_file = os.path.join(settings.DATA_DIR, 'corpus',
        'jp_char_corpus_counts.gz')

#----------------------------------------------------------------------------#

class FlatConfusionModel(object):
    """
    A generic confusion module based on precomputed similarity scores
    between symbols.
    
    Acts as the distribution P(base_form|surface_form), approximated by
    P(surface_form|base_form)P(base_form).
    """
    def __init__(self, data_file):
        self.data_file = data_file
        char_dist = freq.FreqDist.from_file(_char_freq_file)
        freq.smooth_by_adding_one(char_dist)
        
        surface_given_base_dist = self._load_distractors(data_file, char_dist)
        base_given_surface_dist = self._rescore_candidates(
                surface_given_base_dist, char_dist)
        self.dist = base_given_surface_dist

    def prob(self, surface_form, base_form):
        base_dist = self.dist.get(surface_form)
        if base_dist:
            return base_dist.get(base_form, 0.0)
        else:
            return (surface_form == base_form) and 1.0 or 0.0

    def log_prob(self, surface_form, base_form):
        return math.log(self.prob(surface_form, base_form))

    def candidates(self, surface_form):
        """
        Returns a list of (base_form, log_p_base_given_surface) pairs
        containing all known candidates.
        """
        base_dist = self.dist.get(surface_form)
        if base_dist:
            return base_dist.items()
        else:
            return [(surface_form, 0.0)]

    @staticmethod
    def _load_distractors(filename, char_dist):
        """
        Builds and returns the conditional distribution 
        P(surface_form|base_form).
        """
        # First build a map: base -> (surface -> similarity)
        neighbourhoods = {}
        i_stream = sopen(filename)
        for line in i_stream:
            slots = line.rstrip().split()
            base_form = slots.pop(0)
            surface_forms = {base_form: 1.0}
            for surface_form, similarity in ithread(slots):
                similarity = float(similarity)
                assert 0.0 <= similarity <= 1.0

                if similarity == 0.0:
                    continue

                surface_forms[surface_form] = similarity
            assert surface_forms
            neighbourhoods[base_form] = surface_forms

        i_stream.close()
        assert neighbourhoods
        
        # Convert to map: base -> (surface -> probability), using
        # P(surface|base) = P(surface)s(surface, base)/(sum(...)), 
        # i.e. normalised.
        surface_given_base_dist = {}
        for base_form, neighbourhood in neighbourhoods.iteritems():
            surface_dist = {}
            assert neighbourhood
            for neighbour, similarity in neighbourhood.iteritems():
                surface_dist[neighbour] = similarity * \
                        char_dist.prob(neighbour)
            sum_scores = sum(surface_dist.values())
            for surface_form in surface_dist.iterkeys():
                surface_dist[surface_form] /= sum_scores
            
            assert surface_dist
            surface_given_base_dist[base_form] = surface_dist
            
        return surface_given_base_dist
        
    @staticmethod
    def _rescore_candidates(surface_given_base_dist, char_dist):
        """
        Convert our map from a P(surface_form|base_form) distribution to
        an approximation of P(base_form|surface_form), by multiplying each
        value by P(base_form).
        """
        assert char_dist
        new_dist = {}
        log = math.log
        for base_form, surface_dist in surface_given_base_dist.iteritems():
            assert surface_dist
            base_form_prob = char_dist.prob(base_form)
            for surface_form, p_surface_given_base in \
                    surface_dist.iteritems():
                base_dist = new_dist.setdefault(surface_form, {})
                p_base_given_surface = p_surface_given_base * base_form_prob
                base_dist[base_form] = p_base_given_surface
        
        for surface_form, base_dist in new_dist.iteritems():
            sum_probs = sum(base_dist.itervalues())
            assert sum_probs > 0
            for base_form, simple_prob in base_dist.iteritems():
                normalised_prob = simple_prob / sum_probs
                assert 0 < normalised_prob <= 1
                base_dist[base_form] = normalised_prob                
        assert new_dist
        return new_dist

#----------------------------------------------------------------------------#

class WeightedConfusionModel(FlatConfusionModel):
    """
    Acts as the distribution P(base_form|surface_form), approximated by
    P(surface_form|base_form)P(base_form).
    
    Compared to the flat model, we now weight probabilities towards
    surface_form == base_form by using a constant weight parameter in (0, 1).
    """
    def __init__(self, data_file, weight):
        FlatConfusionModel.__init__(self, data_file)
        assert 0 < weight < 1
        self.weight = weight

    def prob(self, surface_form, base_form):
        raw_prob = FlatConfusionModel.prob(self, surface_form, base_form)
        return self._adjust_using_weight(surface_form, base_form, raw_prob)

    def log_prob(self, surface_form, base_form):
        return math.log(self.prob(surface_form, base_form))

    def candidates(self, surface_form):
        raw_candidates = FlatConfusionModel.candidates(self, surface_form)
        adjusted_candidates = []
        for base_form, raw_log_prob in raw_candidates:
            adjusted_log_prob = math.log(self._adjust_using_weight(
                    surface_form, base_form, math.exp(raw_log_prob)))
            adjusted_candidates.append((base_form, adjusted_log_prob))
        return adjusted_candidates
    
    def iterkeys(self):
        return self.dist.iterkeys()

    def _adjust_using_weight(self, surface_form, base_form, raw_prob):
        if (surface_form == base_form):
            return self.weight + (1 - self.weight) * raw_prob
        else:
            return (1 - self.weight) * raw_prob

#----------------------------------------------------------------------------#
