# -*- coding: utf-8 -*-
# 
#  test_confusion_model.py
#  jp-grapheme-alt
#  
#  Created by Lars Yencken on 2008-01-04.
#  Copyright 2008 Lars Yencken. All rights reserved.
# 

import os
import unittest
import doctest

from cjktools.scripts import unique_kanji
from cjktools.common import sopen
from django.conf import settings

import confusion_model

#----------------------------------------------------------------------------#

def suite():
    testSuite = unittest.TestSuite((
            unittest.makeSuite(ConfusionModelTestCase),
            doctest.DocTestSuite(confusion_model)
        ))
    return testSuite

#----------------------------------------------------------------------------#

_allKanji = os.path.join(settings.DATA_DIR, 'lists', 'char', 'jp_jis')

class ConfusionModelTestCase(unittest.TestCase):
    """
    This class tests the ConfusionModel class. 
    """
    def setUp(self):
        filename = os.path.join(settings.DATA_DIR, 'similarity',
                'jyouyou__yehAndLiRadical')
        self.model = confusion_model.WeightedConfusionModel(filename, 0.9)
        pass

    def testConfusion(self):
        for kanji in unique_kanji(sopen(_allKanji).read()):
            candidates = self.model.candidates(kanji)
            self.assertEqual(kanji, max(candidates, key=lambda x: x[1])[0])
    
    def tearDown(self):
        pass

#----------------------------------------------------------------------------#

if __name__ == "__main__":
    unittest.TextTestRunner(verbosity=1).run(suite())

#----------------------------------------------------------------------------#

# vim: ts=4 sw=4 sts=4 et tw=78:
