# -*- coding: utf-8 -*-
#
#  alternation_model.py
#  jp-reading-alt
# 
#  Created by Lars Yencken on 10-04-2009.
#  Copyright 2009 Lars Yencken. All rights reserved.
#

"An abstract phonetic alternation model."


import math

from cjktools import kana_table
from cjktools.exceptions import AbstractMethodError
from django.conf import settings

#----------------------------------------------------------------------------#

class AlternationModelI(object):
    """
    An alternation model provides P(r'|r, k), giving both candidates and
    probabilities for r'.
    """
    def prob(kanji, reading, alternation):
        raise AbstractMethodError

    def log_prob(kanji, reading, alternation):
        raise AbstractMethodError

#----------------------------------------------------------------------------#

class SimpleAlternationModel(AlternationModelI):
    """
    An alternation model based on readings which are subsets of things. To use,
    subclass this model and implement the build_pairs() method.
    """
    #------------------------------------------------------------------------#
    # PUBLIC
    #------------------------------------------------------------------------#

    def __init__(self, alpha):
        self.alpha = alpha
        self.pairs = self.build_pairs()
        map = {}
        for key_a, key_b in self.pairs:
            if key_a in map:
                map[key_a].append(key_b)
            else:
                map[key_a] = [key_b]

            if key_b in map:
                map[key_b].append(key_a)
            else:
                map[key_b] = [key_a]

        self.map = map

    #------------------------------------------------------------------------#

    def log_prob(self, reading, reading_variant):
        """
        Returns the log probability of this variant given the canonical
        reading.
        """
        return math.log(self.prob(reading, reading_variant))

    #------------------------------------------------------------------------#

    def prob(self, reading, reading_variant):
        """
        Returns the probability of the given reading variant being shown
        given the canonical reading.
        """
        uniform_prob = 1.0 / self._num_variants(reading)
        if reading == reading_variant:
            return (1 - self.alpha) + self.alpha * uniform_prob
        else:
            return self.alpha * uniform_prob

    #------------------------------------------------------------------------#

    def candidates(self, kanji, reading):
        """
        Return a list of potential reading variant candidates for this
        model.
        """
        variants = [reading]
        if reading in self.map:
            variants.extend(self.map[reading])

        results = []
        for reading_variant in variants:
            results.append(
                    (reading_variant, self.log_prob(reading, reading_variant))
                )

        return results

    #------------------------------------------------------------------------#
    # PRIVATE
    #------------------------------------------------------------------------#

    def build_pairs(self):
        """
        Builds a list of (short form, long form) pairs for this type of
        alternation.
        """
        raise AbstractMethodError

    #------------------------------------------------------------------------#

    def _num_variants(self, reading):
        """
        Returns the number of variants for this particular reading.

        Sometimes calculating this is useful without generating the
        actual candidate list, which might be exponentially large.
        """
        if reading in self.map:
            return 1 + len(self.map[reading])
        else:
            return 1

    #------------------------------------------------------------------------#

#----------------------------------------------------------------------------#

class VowelLengthModel(SimpleAlternationModel):
    """
    An alternation model for vowel length.
    """
    def __init__(self):
        SimpleAlternationModel.__init__(self, settings.VOWEL_LENGTH_ALPHA)

    def build_pairs(self):
        """
        Builds a correspondence between palatalized and unpalatalized forms
        of kana.
        """
        vowel_pairs = {
                u'あ': u'あ',
                u'い': u'い',
                u'う': u'う',
                u'え': u'い',
                u'お': u'う',
            }

        vowel_to_y_form = {
                u'あ':  u'ゃ',
                u'う':  u'ゅ',
                u'お':  u'ょ',
            }

        table = kana_table.KanaTable.get_cached()
        pairs = []
        for consonant in table.consonants:
            if consonant == u'あ':
                # Plain vowels double in Japanese.
                for vowel, long_vowel in vowel_pairs:
                    pairs.append((vowel, 2*vowel))

            else:
                # Other consonants are more limited.
                for vowel, long_vowel in vowel_pairs.iteritems():
                    kana = table.from_coords(consonant, vowel)
                    pairs.append((kana, kana + long_vowel))

                y_prefix = table.from_coords(consonant, u'い')
                assert y_prefix
                for vowel, y_suffix in vowel_to_y_form.iteritems():
                    long_vowel = vowel_pairs[vowel]
                    pairs.append((
                            y_prefix + y_suffix,
                            y_prefix + y_suffix + long_vowel,
                        ))

        return pairs

    #------------------------------------------------------------------------#

    @classmethod
    def get_cached(cls):
        if not hasattr(cls, '_cached'):
            cls._cached = cls()
        return cls._cached

    #------------------------------------------------------------------------#

#----------------------------------------------------------------------------#

class PalatalizationModel(SimpleAlternationModel):
    """
    A probability model of palatalization for Japanese.
    """

    #------------------------------------------------------------------------#

    def __init__(self):
        SimpleAlternationModel.__init__(self, settings.PALATALIZATION_ALPHA)

    #------------------------------------------------------------------------#

    def build_pairs(self):
        """
        Builds a correspondence between palatalized and unpalatalized forms
        of kana.
        """
        vowel_to_y_form = {
                u'あ':  u'ゃ',
                u'う':  u'ゅ',
                u'お':  u'ょ',
            }

        table = kana_table.KanaTable.get_cached()
        pairs = []
        for consonant in table.consonants:
            i_form = table.from_coords(consonant, u'い')
            for vowel in u'あうお':
                base_form = table.from_coords(consonant, vowel)
                y_form = i_form + vowel_to_y_form[vowel]
                pairs.append((base_form, y_form))

        return pairs

    #------------------------------------------------------------------------#

    @classmethod
    def get_cached(cls):
        if not hasattr(cls, '_cached'):
            cls._cached = cls()
        return cls._cached

    #------------------------------------------------------------------------#

#----------------------------------------------------------------------------#
