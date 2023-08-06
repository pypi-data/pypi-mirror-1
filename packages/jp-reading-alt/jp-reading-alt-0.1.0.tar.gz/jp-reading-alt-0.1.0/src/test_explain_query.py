# -*- coding: utf-8 -*-
#
#  test_explain_query.py
#  jp-reading-alt
# 
#  Created by Lars Yencken on 10-04-2009.
#  Copyright 2009 Lars Yencken. All rights reserved.
#

import unittest
import doctest

import explain_query

#----------------------------------------------------------------------------#

def suite():
    testSuite = unittest.TestSuite((
            unittest.makeSuite(ExplainQueryTestCase),
            doctest.DocTestSuite(explain_query)
        ))
    return testSuite

#----------------------------------------------------------------------------#

class ExplainQueryTestCase(unittest.TestCase):
    """
    This class tests the _explain_query class. 
    """
    def setUp(self):
        pass

    def testNonCompositional(self):
        "Tests bug #10: incorrect error categorisation."
        target = u'海豚'
        query = u'うみぶた'
        real_readings = [u'いるか']
        self.assertEqual(
                explain_query.error_types(target, query, real_readings),
                set([explain_query.QueryError.NonCompositionalReading]),
            )

    def testWithSpaces(self):
        target = u'海豚'
        query = u'うみ ぶた'
        real_readings = [u'いるか']
        self.assertEqual(
                explain_query.error_types(target, query, real_readings),
                set([explain_query.QueryError.NonCompositionalReading]),
            )
    
    def testIncorrectReading(self):
        target = u'今日'
        query = u'いまにち'
        real_readings = [u'きょう', u'こんにち']
        self.assertEqual(
                explain_query.error_types(target, query, real_readings),
                set([explain_query.QueryError.ChoiceOfReading]),
            )
    
    def testVowelLength(self):
        target = u'東京'
        query = u'ときょ'
        real_readings = [u'とうきょう']
        self.assertEqual(
                explain_query.error_types(target, query, real_readings),
                set([explain_query.QueryError.VowelLength]),
            )
        
    def testSequentialVoicing(self):
        target = u'辞書'
        query = u'じじょ'
        real_readings = [u'じしょ']
        self.assertEqual(
                explain_query.error_types(target, query, real_readings),
                set([explain_query.QueryError.SequentialVoicing]),
            )

    def testSoundEuphony(self):
        target = u'学期'
        query = u'がくき'
        real_readings = [u'がっき']
        self.assertEqual(
                explain_query.error_types(target, query, real_readings),
                set([explain_query.QueryError.SoundEuphony]),
            )
    
    def testPalatalization(self):
        target = u'選挙'
        query = u'せんこ'
        real_readings = [u'せんきょ']
        self.assertEqual(
                explain_query.error_types(target, query, real_readings),
                set([explain_query.QueryError.Palatalisation]),
            )
            
    def tearDown(self):
        pass

#----------------------------------------------------------------------------#

if __name__ == "__main__":
    unittest.TextTestRunner(verbosity=1).run(suite())

#----------------------------------------------------------------------------#

# vim: ts=4 sw=4 sts=4 et tw=78:

