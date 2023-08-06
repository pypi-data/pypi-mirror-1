# -*- coding: utf-8 -*-
#----------------------------------------------------------------------------#
# okuriganaModel.py
# Lars Yencken <lars.yencken@gmail.com>
# vim: ts=4 sw=4 sts=4 et tw=78:
# Thu Sep  1 16:17:52 EST 2005
#
#----------------------------------------------------------------------------#

""" This module provides the OkuriganaModel class.
"""

#----------------------------------------------------------------------------#

from os import path
import cPickle as pickle
import re

from cjktools import scripts, smartCache, enum
from cjktools.sequences import *
from cjktools.common import sopen

from entry import Entry
from readingModel import ReadingModel

#----------------------------------------------------------------------------#

OkuriType = enum.Enum('verb', 'kanjidic', 'cooccurrence')
VerbType = enum.Enum('ichidan', 'godan', 'suru', 'irregular')

#----------------------------------------------------------------------------#

def potentialOkurigana(entry):
    """ Determines whether this entry has any potential sites for
        okurigana.
    """
    assert entry.alignment, "How can an empty entry have okurigana?"
    hiragana = scripts.Script.Hiragana
    kanji = scripts.Script.Kanji

    gSegments = entry.alignment[0]

    lastSegmentType = hiragana
    for i in range(len(gSegments)):
        segmentType = scripts.scriptType(gSegments[i])

        if segmentType == hiragana and lastSegmentType == kanji:
            # potential okurigana case
            return True

        lastSegmentType = segmentType
    else:
        # exhausted this entry, no possible okurigana
        return False

#----------------------------------------------------------------------------#

def alignmentHasOkurigana(gSegments, pSegments):
    """ Returns True if the given alignment has okurigana in it, False
        otherwise.
    """
    for seg in gSegments:
        if len(scripts.scriptBoundaries(seg)) > 1:
            return True
    else:
        return False

#----------------------------------------------------------------------------#

def removeOkurigana(gSegments, pSegments):
    """ Removes all okurigana from the segmentation.
    """
    new_gSegments = ()
    new_pSegments = ()

    i = 0
    while i < len(gSegments):
        boundaries = scripts.scriptBoundaries(gSegments[i])
        if len(boundaries) == 1:
            new_gSegments += (gSegments[i],)
            new_pSegments += (pSegments[i],)
            i += 1
        elif len(boundaries) == 2:
            kanjiPart, kanaPart = boundaries
            if i == len(gSegments)-1 or scripts.scriptType(kanaPart) != \
                    scripts.scriptType(gSegments[i+1]):
                # last segment, or differing segments
                new_gSegments += (kanjiPart, kanaPart)
                new_pSegments += (pSegments[i][:-len(kanaPart)],
                        pSegments[i][-len(kanaPart):])
                i += 1
            else:
                # more segments, join with the next segment
                new_gSegments += (kanjiPart, kanaPart + gSegments[i+1])
    
                new_pSegments += (pSegments[i][:-len(kanaPart)],
                        pSegments[i][-len(kanaPart):] + pSegments[i+1])

                i += 2
        else:
            raise Exception, "Too many scripts per segment in %s" % gSegments

    return new_gSegments, new_pSegments

#----------------------------------------------------------------------------#

class OkuriganaModel:
    """ This class provides a verb-conjugation model for GP alignment.
    """
    #------------------------------------------------------------------------#
    # PUBLIC METHODS
    #

    def __init__(self, options):
        """ Creates a new instance by parsing edict for verb conjugation
            entries.
        """
        print "Creating a new okurigana model"
        cacheFile = path.join(settings.CACHE_DIR, 'okuriganaModel.cache')
        edictFile = path.join(settings.DATA_DIR, 'edict.bz2')

        print '--> Cooccurrence threshold set to %d' % options.okuriThreshold
        self._threshold = options.okuriThreshold

        fetchOkurigana = smartCache.diskProxyDirect(
                self._rebuildOkurigana,
                dependencies=['okuriganaModel.py', edictFile],
            )
        self._okurigana = fetchOkurigana(edictFile, threshold=self.threshold)

        self._evaluationRun = not bool(options.inputFile)
        self._simpleMode = bool(options.simpleOkurigana)

        # switches to change behaviour
        self._useKanjidic = options.useKanjidic
        self._useCooccurrence = options.useCooccurrence
        self._useVerbs = options.useVerbs

        self._nFixed = 0
        return


    #------------------------------------------------------------------------#

    def okuriganaAdjustments(self, inputFile, outputFile):
        """ Reparses the entries in the given file and makes okurigana
            adjustments where necessary.
        """
        if self._evaluationRun:
            # read the evaluation input (guaranteed correctly aligned)
            entryIter = self._evaluationInputIter(inputFile)
        else:
            # read regular input from the alignment run (may not be correctly
            # aligned)
            entryIter = self._resultsInputIter(inputFile)

        oStream = sopen(outputFile, 'w')

        for entry in entryIter:
            origAlignment = ' '.join((entry.gString_original, entry.pString))
            if potentialOkurigana:
                # potential site, attempt to solve it
                if self._simpleMode:
                    self._solveSimply(entry)
                else:
                    self._solveOkurigana(entry)

            newAlignment = entry.alignment
            
            print >> oStream, ':'.join((
                    origAlignment,
                    ' '.join(map(lambda x: '|'.join(x), newAlignment))
                ))

        print '--> %d cases had shifted alignments' % self._nFixed

        oStream.close()

        return

    #------------------------------------------------------------------------#

    #------------------------------------------------------------------------#
    # PRIVATE METHODS
    #

    def _parseEdictEntries(self, edictFile):
        """ Parses a single edict entry for a verb.
        """
        iStream = codecs.getreader('utf8')(BZ2File(edictFile, 'r'))

        okurigana = {}
        counts = {}

        for line in iStream:
            if not scripts.hasKanji(line):
                continue

            gString = line.split()[0]

            # update counts for okurigana clustering
            self._updateCooccurrence(gString, counts)

            # look for verbSpecific okurigana
            self._parseVerbDetails(gString, line, okurigana)

        iStream.close()

        self._addCooccurrenceOkurigana(counts, okurigana)

        return okurigana
    
    #------------------------------------------------------------------------#

    @staticmethod
    def _rebuildOkurigana(filename):
        okuriganaMap = self._parseEdictEntries(filename)

        readingModel = ReadingModel()
        extraOkurigana = readingModel.getOkurigana()
        self._addKanjidicOkurigana(extraOkurigana, okuriganaMap)
        return okuriganaMap

    #------------------------------------------------------------------------#

    def _parseVerbDetails(self, gString, line, okurigana):
        """ Determine whether this line defines a verb, and if so grab it's
            details for conjugation.
        """
        verbTag = re.compile('\((.*,)*v(.*)\)')
        kanjiScript = scripts.Script.Kanji

        tagsFound = verbTag.search(line)
        if not tagsFound:
            return

        tag = tagsFound.group(2)

        if tag.endswith('-s'):
            # FIXME ignore special cases for now
            return

        if tag == '1':
            verbType = VerbType.ichidan
        elif tag.startswith('5') and len(tag) <= 2:
            verbType = VerbType.godan
        elif tag == 's':
            verbType = VerbType.suru
        else:
            return

        for i in range(len(gString)-1, -1, -1):
            if scripts.scriptType(gString[i]) == kanjiScript:
                lastKanji = gString[i]
                trailingKana = gString[i+1:]
                baseEntry = (trailingKana, verbType)

                if not okurigana.has_key(lastKanji):
                    okurigana[lastKanji] = set()

                okurigana[lastKanji].add((trailingKana, OkuriType.verb, 
                        verbType))

                break
        else:
            raise Exception, 'Error parsing grapheme string:' + `gString`

        return
    #------------------------------------------------------------------------#

    def _addCooccurrenceOkurigana(self, counts, okurigana):
        """ Add okurigana cases based on cooccurrence, thresholded to some
            value.
        """
        keptItems = filter(lambda x: x[1] >= self._threshold, counts.items())

        counts = dict(keptItems)

        for gString, pString in counts.iterkeys():
            key = gString[-1]
            thisSet = okurigana.setdefault(key, set())
            okurigana[key].add((pString, OkuriType.cooccurrence, None))

        return

    #------------------------------------------------------------------------#

    @staticmethod
    def _addKanjidicOkurigana(kanjidicOkurigana, okuriganaMap):
        """ Adds okurigana from kanjidic into the full class dictionary of
            okurigana instances.
        """
        for kanji, okurigana in kanjidicOkurigana.iteritems():
            possibleOkurigana = okuriganaMap.setdefault(kanji, set())
            for case in okurigana:
                possibleOkurigana.add((case, OkuriType.kanjidic, None))

        return

    #------------------------------------------------------------------------#

    def _addEndings(self, item, endings):
        return map(lambda x: item + x, endings)

    #------------------------------------------------------------------------#

    def _updateCooccurrence(self, gString, counts):
        """ Updates counts for each okurigana occurence.
        """

        kanjiScript = scripts.Script.Kanji
        hiraganaScript = scripts.Script.Hiragana
    
        segments = list(scripts.scriptBoundaries(gString))
        segments.reverse()

        lastSeg = segments.pop()
        lastSegType = scripts.scriptType(lastSeg)

        while segments:
            thisSeg = segments.pop()
            thisSegType = scripts.scriptType(thisSeg)

            if thisSegType == hiraganaScript and lastSegType == kanjiScript:
                feature = lastSeg, thisSeg

                counts[feature] = counts.get(feature, 0) + 1

            lastSeg = thisSeg
            lastSegType = thisSegType

        return

    #------------------------------------------------------------------------#

    def _conjugate(self, kanaEnding, verbType):
        """ Returns a list of conjugates of the verb given.
        """
        if verbType == VerbType.ichidan:
            assert kanaEnding.endswith(u'る')
            base = kanaEnding[:-1]

            conjugates = self._addEndings(
                    base,
                    [u'て', u'る', u'た', u'ない', u'られる', u'られた',
                    u'られない', u'られて']
                )

            if len(kanaEnding) > 1:
                conjugates.append(base)

        elif verbType == VerbType.suru:
            if kanaEnding.endswith(u'する'):
                kanaEnding = kanaEnding[:-2]

            conjugates = self._addEndings(
                    kanaEnding,
                    [u'する', u'します', u'して', u'した', u'しない']
                )

        elif verbType == VerbType.godan:
            lastChar = kanaEnding[-1]
            realBase = kanaEnding[:-1]

            assert scripts.isLine(lastChar, u'う')
            conjugates = [kanaEnding]

            masuBase = realBase + scripts.toLine(lastChar, u'い')
            conjugates.append(masuBase)
            conjugates.append(masuBase + u'ます')

            if lastChar in u'いちり':
                conjugates.extend([realBase + u'って', realBase + u'った'])
            elif lastChar in u'みび':
                conjugates.extend([realBase + u'んで', realBase + u'んだ'])
            elif lastChar == u'き':
                conjugates.append(realBase + u'いて')
            elif lastChar == u'ぎ':
                conjugates.append(realBase + u'いで')

        return conjugates

    #------------------------------------------------------------------------#

    def _evaluationInputIter(self, filename):
        """ Provide an iterator over the evaluation input.
        """
        iStream = sopen(filename, 'r')

        toSegments = lambda x: tuple(x.split('|'))

        for line in iStream:
            line = line.strip()

            # we don't care about the correct entries at this stage, so just
            # get the pre-aligned input
            alignedInput, _correctTarget = line.split(':')[:2]

            gString, pString = alignedInput.split()
            gSegments = toSegments(gString)
            pSegments = toSegments(pString)

            assert gSegments and pSegments

            newEntry = Entry(gString, pString)
            newEntry.aligned = True
            newEntry.alignment = gSegments, pSegments

            yield newEntry

        iStream.close()

        return

    #------------------------------------------------------------------------#


    def _resultsInputIter(self, filename):
        """ Iterates over the entries in a results file (directly output from
            the alignment script).
        """
        iStream = sopen(filename, 'r')
        entries = []

        toSegments = lambda x: tuple(x.split('|'))

        for line in iStream:
            line = line.strip()

            # although we also have the unaligned input, ignore it for now
            _unalignedInput, alignedInput = line.split(':')[:2]

            gString, pString = alignedInput.split()
            gSegments = toSegments(gString)
            pSegments = toSegments(pString)

            assert gSegments and pSegments

            newEntry = Entry(gString, pString)
            newEntry.aligned = True
            newEntry.alignment = gSegments, pSegments

            yield newEntry

        iStream.close()

        return

    #------------------------------------------------------------------------#

    def _solveSimply(self, entry):
        """ Resolves this case by simply assuming that every site of potential
            okurigana is okurigana, and just removing all kanji->kana
            boundaries. 
        """
        hiragana = scripts.Script.Hiragana
        kanji = scripts.Script.Kanji

        gSegments = entry.alignment[0]
        i = 1
        while i < len(gSegments):
            lastSegmentType = scripts.scriptType(gSegments[i-1])
            segmentType = scripts.scriptType(gSegments[i])

            if segmentType == hiragana and lastSegmentType == kanji and \
                    gSegments[i] not in (u'の', u'が'):
                # potential okurigana case; solve then move a variable
                # increment
                i += self._shiftSegments(entry, gSegments[i], i)
            else:
                i += 1

            gSegments = entry.alignment[0]

        return

    #------------------------------------------------------------------------#

    def _solveOkurigana(self, entry):
        """ Resolves this case using our full model.
        """
        hiragana = scripts.Script.Hiragana
        kanji = scripts.Script.Kanji

        gSegments = entry.alignment[0]
        i = 1
        while i < len(gSegments):
            lastSegmentType = scripts.scriptType(gSegments[i-1])
            segmentType = scripts.scriptType(gSegments[i])

            if segmentType == hiragana and lastSegmentType == kanji:
                # potential okurigana case; solve then move a variable
                # increment
                i += self._solveSingleCase(entry, i)
            else:
                i += 1

            gSegments = entry.alignment[0]

        return

    #------------------------------------------------------------------------#

    def _solveSingleCase(self, entry, i, default=1):
        """ A potential case of okurigana. Determine if our verb conjugation
            model solves this case.
        """
        assert entry.alignment, "We've got an empty alignment Scotty!!!"
        gSegments, pSegments = entry.alignment

        kanjiIndex = gSegments[i-1][-1]

        if not self._okurigana.has_key(kanjiIndex):
            return default

        baseOkuriOptions = self._okurigana[kanjiIndex]
        kanaOptions = set()
        for trailingKana, okuriType, subType in baseOkuriOptions:
            if okuriType == OkuriType.verb and self._useVerbs:
                # verb okurigana
                kanaOptions.update(self._conjugate(trailingKana, subType))
            elif okuriType == OkuriType.kanjidic and self._useKanjidic:
                # unknown okurigana type from kanjidic
                kanaOptions.add(trailingKana)
            elif okuriType == OkuriType.cooccurrence and self._useCooccurrence:
                # unknown okurigana type from kanjidic
                kanaOptions.add(trailingKana)
            
        # make a list of all potential matches
        potentialHits = []
        for trailingKana in kanaOptions:
            if gSegments[i].startswith(trailingKana):
                potentialHits.append((len(trailingKana), trailingKana))

        if potentialHits:
            # choose the longest match
            matchedKana = max(potentialHits)[1]
        elif gSegments[i] in (u'の', u'が'):
            return default
        else:
            # XXX if we can't match, just match the whole thing =)
            matchedKana = gSegments[i]

        increment = self._shiftSegments(entry, matchedKana, i)

        return increment

    #------------------------------------------------------------------------#

    def _shiftSegments(self, entry, kanaPrefix, i):
        """ Upon finding a clear case of okurigana, this method is called to
            modify the entry.
        """
        assert entry.alignment, "Need a valid alignment to start with"
        gSegments, pSegments = entry.alignment
        self._nFixed += 1

        sharedSegments = zip(gSegments, pSegments)

        thisSeg = sharedSegments[i]
        lastSeg = sharedSegments[i-1]

        if len(thisSeg[1]) == len(kanaPrefix):
            # simply remove this segment boundary
            newSeg = lastSeg[0] + thisSeg[0], lastSeg[1] + thisSeg[1]

            newSegments = sharedSegments[:i-1] + [newSeg] + sharedSegments[i+1:]

            entry.alignment = map(tuple, unzip(newSegments))

            return 0
        else:
            # shift the segment boundary
            shiftSize = len(kanaPrefix)

            (gSegA, gSegB), (pSegA, pSegB) = unzip((lastSeg,thisSeg))
            gSegA += gSegB[:shiftSize]
            gSegB = gSegB[shiftSize:]
            pSegA += pSegB[:shiftSize]
            pSegB = pSegB[shiftSize:]

            lastSeg, thisSeg = zip([gSegA, gSegB], [pSegA, pSegB])

            newSegments = sharedSegments[:i-1] + [lastSeg, thisSeg] + \
                    sharedSegments[i+1:]

            entry.alignment = map(tuple, unzip(newSegments))

            return 1

    #------------------------------------------------------------------------#

#----------------------------------------------------------------------------#
