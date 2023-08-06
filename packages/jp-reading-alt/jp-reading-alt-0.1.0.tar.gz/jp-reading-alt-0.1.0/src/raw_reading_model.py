# -*- coding: utf-8 -*-
#
#  raw_reading_model.py
#  jp-reading-alt
# 
#  Created by Lars Yencken on 10-04-2009.
#  Copyright 2009 Lars Yencken. All rights reserved.
#

"A raw reading model, without any normalization."

from os.path import join

from cjktools.common import sopen
from cjktools.smart_cache import disk_proxy_direct
from cjktools import scripts
from django.conf import settings
from simplestats import ConditionalFreqDist

#----------------------------------------------------------------------------#

_edict_aligned_file = join(settings.DATA_DIR, 'aligned',
        'je_edict.aligned.gz')

_seg_separator = '|'
_entry_separator = ':'
_gp_separator = ' '

#----------------------------------------------------------------------------#

class RawReadingModel(ConditionalFreqDist):
    """
    A reading model based on exact segment counts, without normalization.
    """
    #------------------------------------------------------------------------#
    # PUBLIC METHODS
    #------------------------------------------------------------------------#

    def __init__(self):
        """
        Constructor. Loads all counts from the aligned Edict dictionary.
        """
        ConditionalFreqDist.__init__(self)

        kanji_script = scripts.Script.Kanji
        i_stream = sopen(_edict_aligned_file, 'r')
        for line in i_stream:
            original, alignment = line.rstrip().split(_entry_separator)
            grapheme_segs, phoneme_segs = alignment.split(_gp_separator)
            grapheme_segs = grapheme_segs.split(_seg_separator)
            phoneme_segs = scripts.to_hiragana(phoneme_segs).split(
                    _seg_separator)
            
            segments = [
                    Segment(g, p) \
                    for (g,p) in zip(grapheme_segs, phoneme_segs) \
                    if kanji_script in scripts.script_types(g) \
                ]
            for segment in segments:
                self.inc(segment.graphemes, segment.phonemes)

        i_stream.close()

        return

    #------------------------------------------------------------------------#

    @classmethod
    def get_cached(cls):
        """
        Return a memory or disk cached copy. If neither of these is
        available, generate a new copy.
        """
        if not hasattr(cls, '_cached'):
            fetch_kanjidic = disk_proxy_direct(
                    RawReadingModel,
                    join(settings.CACHE_DIR, 'rawReadingModel.cache'),
                    dependencies=[__file__, _edict_aligned_file],
                )
            cls._cached = fetch_kanjidic()

        return cls._cached

#----------------------------------------------------------------------------#

class Segment(object):
    """
    A basic data structure representing grapheme string aligned to a phoneme
    string.
    """
    __slots__ = ('graphemes', 'phonemes')

    def __init__(self, g, p):
        self.graphemes = g
        self.phonemes = p

    def __unicode__(self):
        return u'%s:%s' % (self.graphemes, self.phonemes)

    def __hash__(self):
        return hash((self.graphemes, self.phonemes))

    def __cmp__(self, rhs):
        return cmp(
                (self.graphemes, self.phonemes),
                (rhs.graphemes, rhs.phonemes)
            )

#----------------------------------------------------------------------------#

