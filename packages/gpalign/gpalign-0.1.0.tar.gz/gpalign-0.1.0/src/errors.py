#!/usr/bin/env python
# -*- coding: utf-8 -*-
#----------------------------------------------------------------------------#
# errors.py
# Lars Yencken <lars.yencken@gmail.com>
# vim: ts=4 sw=4 sts=4 et tw=78:
# Wed May 25 23:45:40 EST 2005
#
#----------------------------------------------------------------------------#

import okuriganaModel

from cjktools.common import sopen

#----------------------------------------------------------------------------#

def separateErrors(baseFile):
    """ Separates out the errors from the alignments, and tries to classify
        them.
    """
    newUtfFile = lambda x: sopen(baseFile + x, 'w')

    inputFile = sopen(baseFile, 'r')

    good = set()
    bad = set()
    badOkuri = set()
    badGapping = set()
    badAlign = set()
    badConstrain = set()

    for line in inputFile:
        original, testCase, correctCase = _parseLine(line)

        if testCase == correctCase:
            good.add(line)
            continue

        if testCase == [('???',)]:
            badConstrain.add(line)
            bad.add(line)
            continue

        # the rest of the cases are bad
        if _detectGapping(correctCase):
            badGapping.add(line)
            bad.add(line)
            continue

        if _badAlignment(testCase, correctCase):
            badAlign.add(line)

        elif _badOkurigana(correctCase, testCase):
            badOkuri.add(line)

        bad.add(line)
    
    total = len(good.union(bad))
    badOther = bad.difference(badGapping.union(badAlign).union(badOkuri).union(
            badConstrain))

    _linesToFile(good, '.good', baseFile)
    _linesToFile(bad, '.bad', baseFile)
    _linesToFile(badOkuri, '.bad.okuri', baseFile)
    _linesToFile(badGapping, '.bad.gapping', baseFile)
    _linesToFile(badAlign, '.bad.align', baseFile)
    _linesToFile(badOther, '.bad.other', baseFile)
    _linesToFile(badConstrain, '.bad.constrain', baseFile)

    nGood, nBad, nBadOkuri, nBadGapping, nBadAlign, nUnknown, nConstrain = \
            map(
                len,
                (good, bad, badOkuri, badGapping, badAlign, badOther,
                badConstrain)
            )

    print '%d total alignments' % total
    print '--> %.2f%% correct (%d)' % ((100*nGood / float(total)),nGood)
    print '--> %.2f%% in error (%d)' % ((100*nBad / float(total)),nBad)
    print '----> %.2f%% okurigana (%d)' % ((100*nBadOkuri / float(total)),\
            nBadOkuri)
    print '----> %.2f%% gapping (%d)' % ((100*nBadGapping / float(total)),\
            nBadGapping)
    print '----> %.2f%% align (%d)' % ((100*nBadAlign / float(total)),\
            nBadAlign)
    print '----> %.2f%% overconstrained (%d)' % ((100*nConstrain / \
            float(total)), nConstrain)
    print '----> %.2f%% unknown (%d)' % ((100*(nUnknown)/float(total)),\
            nUnknown)

    return

#----------------------------------------------------------------------------#

def _parseLine(line):
    lineTuple = line.strip().split(':', 2)

    segment = lambda x: tuple(x.strip('|').split('|'))
    lineTuple = map(lambda x: map(segment, x.split(' ',1)), lineTuple)

    return lineTuple

#----------------------------------------------------------------------------#

def _linesToFile(lineSet, extension, baseName):
    oStream = sopen(baseName + extension, 'w')
    oStream.writelines(lineSet)
    oStream.close()
    return 

#----------------------------------------------------------------------------#

def _badAlignment(testCase, correctCase):
    """ Determines whether this case is a bad alignment case.
    """
    gSegments, pSegments = testCase
    cgSegments, cpSegments = correctCase

    if okuriganaModel.alignmentHasOkurigana(cgSegments, cpSegments):
        testCase = okuriganaModel.removeOkurigana(testCase[0], testCase[1])
        correctCase = okuriganaModel.removeOkurigana(correctCase[0],
                correctCase[1])

    return testCase != correctCase

#----------------------------------------------------------------------------#

def _badOkurigana(testCase, correctCase):
    gSegments, pSegments = testCase
    cgSegments, cpSegments = correctCase

    if okuriganaModel.alignmentHasOkurigana(cgSegments, cpSegments):
        if okuriganaModel.alignmentHasOkurigana(gSegments, pSegments):
            return True
        else:
            # we forgot to add okurigana
            return False
    else:
        # have we mistakenly added okurigana?
        return okuriganaModel.alignmentHasOkurigana(gSegments, pSegments)

#----------------------------------------------------------------------------#

def _detectGapping(correctCase):
    """ Determines whether this was a case of grapheme gapping. Tell-tale
        signs: a '<' in the phoneme segment.
    """
    gSegments, pSegments = correctCase
    for segment in pSegments:
        if '<' in segment:
            return True
    else:
        return False

#----------------------------------------------------------------------------#

# vim: ts=4 sw=4 sts=4 et tw=78:
