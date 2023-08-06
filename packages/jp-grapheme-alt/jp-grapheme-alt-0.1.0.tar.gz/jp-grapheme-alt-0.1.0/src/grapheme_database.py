#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
#  grapheme_database.py
#  jp-grapheme-alt
#  
#  Created by Lars Yencken on 2008-01-08.
#  Copyright 2008 Lars Yencken. All rights reserved.
# 

"""
This script builds the grapheme-alternation table which allows character
similarity search to take place.
"""

import os, sys, optparse

from django.db import connection
from django.conf import settings
from cjktools.sequences import groups_of_n_iter
import consoleLog

import confusion_model

#----------------------------------------------------------------------------#
# PUBLIC
#----------------------------------------------------------------------------#

# Location of file giving P(surface_form|base_form) for each surface_form 
# listed.
_similarity_file = os.path.join(settings.DATA_DIR, 'similarity',
                    'jyouyou__strokeEditDistance')
 
dependencies = [__file__, _similarity_file]

log = consoleLog.default

class GraphemeDatabase(object):
    def build(self):
        log.start('Building grapheme tables', nSteps=1)
        log.log('Storing grapheme alternations')
        alt_tree = self._store_alternations()
        log.finish()
        return

    def _store_alternations(self):
        graphicalModel = confusion_model.WeightedConfusionModel(
                _similarity_file, 0.9)
        assert graphicalModel.dist
        rowIter = self._iter_rows(graphicalModel)
        cursor = connection.cursor()
        cursor.execute('DELETE FROM jp_grapheme_alt_graphemealternation')
        for rowGroup in groups_of_n_iter(10000, rowIter):
            cursor.executemany(
                    """
                    INSERT INTO jp_grapheme_alt_graphemealternation
                        (base_form, surface_form, code, probability)
                    VALUES (%s, %s, %s, %s)
                    """,
                    rowGroup
                )
        cursor.close()
        return

    def _iter_rows(self, model):
        for surface_form in model.iterkeys():
            candidates = model.candidates(surface_form)
            if len(candidates) == 1:
                # No candidates other than exact matches; omit from our table.
                continue
                
            for base_form, log_prob in candidates:
                yield base_form, surface_form, 'g', log_prob

#----------------------------------------------------------------------------#

def build():
    db = GraphemeDatabase()
    db.build()
    return
    
#----------------------------------------------------------------------------#
# PRIVATE
#----------------------------------------------------------------------------#

#----------------------------------------------------------------------------#
# MODULE EPILOGUE
#----------------------------------------------------------------------------#

def _create_option_parser():
    usage = \
"""%prog [options]

Build the grapheme confusion tables for FOKS."""

    parser = optparse.OptionParser(usage)

    parser.add_option('--debug', action='store_true', dest='debug',
            default=False, help='Enables debugging mode [False]')

    return parser

#----------------------------------------------------------------------------#

def main(argv):
    parser = _create_option_parser()
    (options, args) = parser.parse_args(argv)

    if args:
        parser.print_help()
        sys.exit(1)

    # Avoid psyco in debugging mode, since it merges stack frames.
    if not options.debug:
        try:
            import psyco
            psyco.profile()
        except:
            pass

    build()

    return

#----------------------------------------------------------------------------#

if __name__ == '__main__':
    main(sys.argv[1:])

#----------------------------------------------------------------------------#
  
# vim: ts=4 sw=4 sts=4 et tw=78:
