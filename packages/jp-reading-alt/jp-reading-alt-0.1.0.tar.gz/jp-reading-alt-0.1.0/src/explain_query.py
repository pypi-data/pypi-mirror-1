# -*- coding: utf-8 -*-
#
#  explain_query.py
#  jp-reading-alt
# 
#  Created by Lars Yencken on 10-04-2009.
#  Copyright 2009 Lars Yencken. All rights reserved.
#

try:
    from itertools import product
except ImportError:
    # Not available yet, must be running python <2.6
    def product(*args, **kwds):
        # product('ABCD', 'xy') --> Ax Ay Bx By Cx Cy Dx Dy
        # product(range(2), repeat=3) --> 000 001 010 011 100 101 110 111
        pools = map(tuple, args) * kwds.get('repeat', 1)
        result = [[]]
        for pool in pools:
            result = [x+[y] for x in result for y in pool]
        for prod in result:
            yield tuple(prod)

from cjktools.scripts import script_type, Script, script_boundaries
from cjktools import enum
from django.db.models import get_model
from hierarchy import model_tree, html_tree

def explain_reading(word, reading):
    """
    Explains how this reading leads us to this word. If no plausible
    explanation is found, the reading is presumed to be unique to the whole
    word. The query link between the reading and the word should have been 
    already tested before this method is called.
    """
    grapheme_segs = _maximally_segment(word)
    
    reading_segs = _segment_reading(grapheme_segs, reading)
    if not reading_segs:
        return _unique_reading(word, reading)
                
    result = []
    for g_seg, r_seg in zip(grapheme_segs, reading_segs):
        if script_type(g_seg) != Script.Kanji:
            result.append('<span class="explanation">%s</span> ' % g_seg)
            continue
        
        alternation = get_model('jp_reading_alt', 'kanjireading'
                ).objects.get(kanji=g_seg, reading=r_seg).reading_alternation
        tree = model_tree.build_path(alternation, 'value')
        tree = _collapse_tree(tree)
        result.append(html_tree.as_html_tree(tree, open_until_depth=100,
                annotate=_annotator))
        
    return result

QueryError = enum.Enum(
        'NonCompositionalReading',
        'SequentialVoicing',
        'SoundEuphony',
        'ChoiceOfReading',
        'VowelLength',
        'Palatalisation',
    )

def error_types(word, query, real_readings):
    """
    Determines what the cause of the error is in the given reading. Needs to
    know the real readings of the word to give an answer.
    """
    query = query.replace(' ', '') # ignore explicit segmentations
    
    if query in real_readings:
        raise ValueError('query is a valid reading')

    grapheme_segs = _maximally_segment(word)    
    for real_reading in real_readings:
        if _segment_reading(grapheme_segs, real_reading):
            break
    
    else:
        # No real readings are compositional, so this error is due to
        # non-compositionality
        return set([QueryError.NonCompositionalReading])
    
    query_segs = _segment_reading(grapheme_segs, query)
    if not query_segs:
        raise ValueError("can't segment query -- shouldn't happen")
        
    reading_segs = _match_real_segments(grapheme_segs, query_segs,
            real_readings)
    if not reading_segs:
        # We didn't align to any real reading, so our reading was bad.
        return set([QueryError.ChoiceOfReading])
    
    KanjiReading = get_model('jp_reading_alt', 'kanjireading')
    
    # We aligned to a real reading, so we can compare segment by segment
    errors = set()
    for g_seg, r_seg, q_seg in zip(grapheme_segs, reading_segs, query_segs):
        if r_seg == q_seg or script_type(g_seg) != Script.Kanji:
            continue
        
        real_seg_reading = KanjiReading.objects.get(kanji=g_seg, 
                reading=r_seg)
        query_seg_reading = KanjiReading.objects.get(kanji=g_seg, 
                reading=q_seg)
        real_alt_set = set(real_seg_reading.alternations)
        query_alt_set = set(query_seg_reading.alternations)
        
        diff_codes = real_alt_set.union(query_alt_set).difference(
                real_alt_set.intersection(query_alt_set))
        
        if not diff_codes:
            # Readings differ, but how?
            if r_seg[1:] == q_seg[1:] and r_seg[0] != q_seg[0]:
                # Looks like voiced variants
                diff_codes = 's'
            else:
                raise Exception('no ostensible difference between readings')
        
        for code in diff_codes:
            if code == 's':
                # 's' is shared between sequential voicing and sound euphony
                if r_seg[:-1] == q_seg[:-1] \
                        and u'っ' in (r_seg[-1], q_seg[-1]):
                    errors.add(QueryError.SoundEuphony)
                else:
                    errors.add(QueryError.SequentialVoicing)
            elif code == 'g':
                errors.add(QueryError.SoundEuphony)
            elif code == 'v':
                errors.add(QueryError.VowelLength)
            elif code == 'p':
                errors.add(QueryError.Palatalisation)
            else:
                raise ValueError('unknown error code "%s"' % code)
    
    return errors

def _match_real_segments(grapheme_segs, query_segs, real_readings):
    """
    Work out if the given query is a minor variant of any of the real 
    readings. If so, return the segments for the real reading; otherwise,
    return None.
    """
    # Can we align this to any single real reading?
    get_reading = get_model('jp_reading_alt', 'kanjireading').objects.get
    for reading in real_readings:
        reading_segs = _segment_reading(grapheme_segs, reading)
        if reading_segs is None:
            # No way to align these segments
            continue
                
        for g_seg, r_seg, q_seg in zip(grapheme_segs, reading_segs, 
                query_segs):
            
            if g_seg == q_seg or script_type(g_seg) != Script.Kanji:
                continue
            
            real_seg_reading = get_reading(kanji=g_seg, reading=r_seg)
            query_seg_reading = get_reading(kanji=g_seg, reading=q_seg)
            if not real_seg_reading.shares_alternation_path(
                    query_seg_reading):
                # Not based on the same reading root -- this pairing is bad
                break
        else:
            # This pairing shared all significant reading roots
            return reading_segs
    
    return None

#----------------------------------------------------------------------------#

def _segment_reading(grapheme_segs, reading):
    """
    Segment the reading in such a way that it matches the grapheme segments,
    or return None.
    """
    # Build list of part candidates
    KanjiReading = get_model('jp_reading_alt', 'kanjireading')
    reading_parts = []
    for g_seg in grapheme_segs:
        if script_type(g_seg) == Script.Kanji:
            reading_parts.append([r.reading for r in
                    KanjiReading.objects.filter(kanji=g_seg)])
        else:
            reading_parts.append([g_seg])
        
    matches = [c for c in product(*reading_parts) if ''.join(c) == 
            reading]
    
    if len(matches) == 0:
        return None
    
    return matches[0] # possibly truncating alternative matches

def _collapse_tree(tree):
    "Reduce a tree to significant differences between child and parent nodes."
    for node in tree.walk_preorder():
        if node.parent:
            node.attrib['diff_codes'] = set(node.attrib['code']
                    ).difference(node.parent.attrib['code'])
        else:
            node.attrib['diff_codes'] = None
            
    for node in tree.walk_postorder():
        if not node.children:
            continue
        
        for key, child in node.children.items():
            if not child.attrib['diff_codes']:
                # Prune this child, taking its children first
                if child.children:
                    for grand_key, grand_child in child.children.items():
                        assert grand_key not in node.children
                        node.children[grand_key] = grand_child
                
                del node.children[key]

    return tree

def _unique_reading(word, reading):
    return u'This is a unique reading of %s, not based on its parts.</p>' %\
            word

_diff_code_verbose = {
        'b':        'base reading',
        'p':        'palatalization error',
        's':        'voicing or gemination alternation',
        'v':        'vowel error',
    }

def _annotator(node):
    diff_code, = list(node.attrib['diff_codes'])
    if diff_code == 'k':
        return u'<span class="explanation">%s</span>' % node.label
    
    explanation = _diff_code_verbose[diff_code]
    if diff_code == 's':
        if node.label.endswith(u'っ'):
            explanation = 'sound euphony'
        else:
            explanation = 'sequential voicing'
    
    return u'<span class="explanation">%s (%s)</span>' % (
            node.label, explanation)

def _maximally_segment(word):
    """
    Splits the word into segments, such that each kanji is in its own
    segment and consecutive kana are grouped into one segment.
    """
    # Firstly insert boundaries for each script change.
    wordSegs = script_boundaries(word)

    # Secondly, add boundaries between consecutive kanji.
    output_segs = []
    for segment in wordSegs:
        if script_type(segment) == Script.Kanji:
            output_segs.extend(segment)
        else:
            output_segs.append(segment)

    return output_segs
