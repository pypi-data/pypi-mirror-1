# -*- coding: utf-8 -*-
#----------------------------------------------------------------------------#
# potentials.py
# Lars Yencken <lars.yencken@gmail.com>
# vim: ts=4 sw=4 sts=4 et tw=78:
# Sun May 15 22:41:16 EST 2005
#----------------------------------------------------------------------------#

""" This module is responsible for generating all possible segmentations for
    each grapheme string/phoneme string pair. The main method exported is the
    generateAlignments() method.
"""

#----------------------------------------------------------------------------#

from os import path
import string
import sys

from cjktools import scripts, kanaTable
from cjktools.common import sopen

import stats
import potentials
import settings

#----------------------------------------------------------------------------#
# PUBLIC METHODS
#

def generateAlignments(entries, options):
    """ Generates all possible alignments for each entry/reading pair in the
        input list.

        @param entries: A list of (grapheme string, phoneme string) pairs.
        @type entries: [(str, str)]
        @return: A pair (unique alignments, ambiguous alignments) where the
        second member is a list of (graphemeString, [potentialAlignments]).
    """
    # we record anything which we've overconstrained and can't solve
    overconstrained = sopen(path.join(settings.LOG_DIR, 'overconstrained'),
            'w')

    uniqueEntries = []
    ambiguousEntries = []

    for entry in entries:
        _addAlignmentsToEntry(entry, options)

        if entry.aligned:
            uniqueEntries.append(entry)
            continue

        if entry.potentials:
            ambiguousEntries.append(entry)
        else:
            # we've overconstrained this entry -- no potential alignments
            print >> overconstrained, entry.toString()
    
    return uniqueEntries, ambiguousEntries

#----------------------------------------------------------------------------#

#----------------------------------------------------------------------------#
# PRIVATE METHODS
#

def _addAlignmentsToEntry(entry, options):
    """ Determine all possible kanji/reading segmentations and aligments,
        taking linguistic constraints into account.
    """
    # work out all the ways the grapheme string can vary
    partialAlignments = _graphemeAlignments(entry.gString)

    if len(partialAlignments) > 0.75*options.maxPotentials:
        # too many alignments
        return

    # for each grapheme variation, work out possible phonetic alignments
    finalAlignments = _phonemeAlignments(entry.pString, partialAlignments,
            options)

    if len(finalAlignments) > options.maxPotentials:
        # too many alignments
        return

    assert len(set(finalAlignments)) == len(finalAlignments), \
            "duplicate alignments detected"

    if len(finalAlignments) == 1:
        entry.aligned = True
        entry.alignment = finalAlignments[0]
    else:
        entry.potentials = finalAlignments

    return

#----------------------------------------------------------------------------#

def _graphemeAlignments(gString):
    """ Determine all possible segmentations of the mixed script entry string
        only, leaving the hiragana reading string untouched for now.
    """
    kanjiScript = scripts.Script.Kanji
    combinationSets = []
    for segment in scripts.scriptBoundaries(gString):
        if len(segment) > 1 and scripts.scriptType(segment) == kanjiScript:
            combinationSets.append(stats.segmentCombinations(segment))
        else:
            combinationSets.append([(segment,)])
    
    alignments = stats.combinationTuples(combinationSets)

    return alignments

#----------------------------------------------------------------------------#

def _phonemeAlignments(pString, partialAlignments, options):
    """ For each segmented kanji string, this method segments the reading to
        match.
    """
    alignments = []
    for graphemeSegments in partialAlignments:
        alignments.extend(_matchGraphemeSegments(pString, graphemeSegments))
    
    alignments = _pruneAlignments(alignments, options)

    return alignments

#----------------------------------------------------------------------------#

def _matchGraphemeSegments(pString, gSegments):
    """ Creates one or more segmentations which match the kanji segments with
        the reading string.
    """
    kanjiScript = scripts.Script.Kanji

    # where there's only one segment, no worries
    numSegments = len(gSegments)
    if numSegments == 1:
        pSegments = (pString,)
        return [(gSegments, pSegments)]

    pSegmentsList = [((), pString)]
    for i in range(numSegments):
        gSegment = gSegments[i]
        # FIXME is this needed? finalSegment = (numSegments == i+1)

        if scripts.scriptType(gSegment) == kanjiScript:
            pSegmentsList = _alignKanjiSegment(gSegment, pSegmentsList, i,
                    numSegments)
        else:
            pSegmentsList = _alignKanaSegment(gSegment, pSegmentsList)
    
    # filter out those with remaining unaligned phonemes
    alignments = [(gSegments, x) for (x,y) in pSegmentsList if y == '']

    return alignments

#----------------------------------------------------------------------------#

def _alignKanjiSegment(gSegment, pSegmentsList, i, numSegments):
    """ Align an individual kanji segment with each of several possible
        phoneme alignments.
    """
    nextLevelSegments = []

    # for each potential, generate many possible alignments
    for existingSegments, remainingReading in pSegmentsList:
        # at least one phoneme for every grapheme
        maxSegLength = len(remainingReading) + i - numSegments + 1
        minSegLength = len(gSegment)

        # add a possible alignment for each slice of kana pie
        for j in range(minSegLength, maxSegLength+1):
            newSegments = existingSegments + (remainingReading[:j],)
            newRemainingReading = remainingReading[j:]
            nextLevelSegments.append((newSegments, newRemainingReading))
    
    return nextLevelSegments

#----------------------------------------------------------------------------#

def _alignKanaSegment(gSegment, pSegmentsList):
    """ Align with a kana segment, which has to match up with itself. Discard
        any potential alignments where this kana doesn't match up.
    """
    segLen = len(gSegment)

    nextLevelSegments = []
    for pSegments, pString in pSegmentsList:
        if pString[:segLen] == gSegment:
            pSegments += (gSegment,)
            pString = pString[segLen:]
            nextLevelSegments.append((pSegments, pString))

    return nextLevelSegments

#----------------------------------------------------------------------------#

def _pruneAlignments(alignments, options):
    """ Applies additional constraints to the list of alignments, returning a
        subset of that list.
    """
    kanjiScript = scripts.Script.Kanji
    keptAlignments = []
    for kanjiSeg, readingSeg in alignments:
        assert len(kanjiSeg) == len(readingSeg)
        for i in range(len(readingSeg)):
            rSeg = readingSeg[i]
            kSeg = kanjiSeg[i]

            # don't allow reading segments to start with ゅ or ん
            if scripts.scriptType(kSeg) == kanjiScript and \
                    (rSeg[0] == kanaTable.nKana or rSeg[0] in kanaTable.smallKana):
                break

            # don't allow kanji segments with more than 4 kana per kanji
            rSegShort = filter(lambda x: x not in kanaTable.smallKana, rSeg)
            maxLength = options.maxPerKanji*len(kSeg)
            if scripts.scriptType(kSeg) == kanjiScript and \
                    len(rSegShort) > maxLength:
                break
        else:
            keptAlignments.append((kanjiSeg, readingSeg))

    return keptAlignments

#----------------------------------------------------------------------------#

#----------------------------------------------------------------------------#

def segmentToString(segment):
    return string.join(segment, '|')

#----------------------------------------------------------------------------#

def alignmentToString(alignment):
    return segmentToString(alignment[0]) +' - '+ segmentToString(alignment[1])

#----------------------------------------------------------------------------#

def printSegment(segment, stream=sys.stdout):
    print >> stream, string.join(segment, '|')
    return

#----------------------------------------------------------------------------#

def printAlignment(alignment, stream=sys.stdout):
    print >> stream, '|'.join(alignment[0]) + ' - ' + '|'.join(alignment[1])
    return

#----------------------------------------------------------------------------#

