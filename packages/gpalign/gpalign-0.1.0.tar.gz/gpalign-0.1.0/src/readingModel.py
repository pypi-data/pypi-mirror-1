# -*- coding: utf-8 -*-
#----------------------------------------------------------------------------#
# readingModel.py
# Lars Yencken <lars.yencken@gmail.com>
# vim: ts=4 sw=4 sts=4 et tw=78:
# Thu Aug 18 13:03:38 EST 2005
#
#----------------------------------------------------------------------------#

from os import path
import cPickle as pickle

from cjktools import scripts, smartCache, enum, alternations
from cjktools.sequences import *
from cjktools.common import sopen

from entry import Entry
import settings

#----------------------------------------------------------------------------#

class PathException(Exception): pass

#----------------------------------------------------------------------------#

ReadingLoc = enum.Enum('any', 'prefix', 'suffix')
ReadingType = enum.Enum('on', 'kun', 'unknown')
ReadingKnowledge = enum.Enum('known', 'trial')

#----------------------------------------------------------------------------#

class ReadingModel:
    """ A model of the readings that each kanji takes, and some additional
        information on their reliability. 
    """

    #------------------------------------------------------------------------#
    # PUBLIC METHODS
    #

    def __init__(self):
        """ Creates a new instance, populating it with kanjidic's model. The
            initial model gets cached, so we don't have to get any
            differences.
        """
        print 'Initialising reading model'
        cacheFile = path.join(settings.CACHE_DIR, 'readingModel.cache')
        dictFiles = [path.join(settings.DATA_DIR, d) for d in (
                'kanjidic.bz2', 'kanjd212.bz2')]
        self._readings = {}
        self._pool = {}
        self._okuri = {}
        
        fetchModel = smartCache.diskProxyDirect(
                self._parseKanjiDics,
                cacheFile,
                dependencies=[__file__] + list(dictFiles),
            )
        model = fetchModel(dictFiles)

        self._readings, self._pool, self._okuri = model

        return

    #------------------------------------------------------------------------#

    def pruneAlignments(self, ambiguousEntries):
        """ Prunes potential alignments away from entries where.
        """
        unique = []
        ambiguous = []
        kanjiScript = scripts.Script.Kanji
        for entry in ambiguousEntries:
            remainingAlignments = []

            for gSegments, pSegments in entry.potentials:
                for i in xrange(len(gSegments)):
                    if not scripts.scriptType(gSegments[i]) == kanjiScript:
                        continue

                    if not self._validateReading(gSegments[i], pSegments[i]):
                        # hit a bad reading, skip this alignment
                        break
                else:
                    # all readings matched
                    remainingAlignments.append((gSegments, pSegments))

            if not remainingAlignments:
                # this method failed, fallback to previous method
                ambiguous.append(entry)
            elif len(remainingAlignments) == 1:
                # success, disambiguated
                entry.potentials = []
                [entry.alignment] = remainingAlignments
                entry.aligned = True
                unique.append(entry)
            else:
                # success, partially disambiguated
                entry.potentials = remainingAlignments
                ambiguous.append(entry)

        return unique, ambiguous

    #------------------------------------------------------------------------#

    def getOkurigana(self):
        return self._okuri

    #------------------------------------------------------------------------#
    # PRIVATE METHODS
    #

    def _validateReading(self, grapheme, phoneme):
        """ Checks whether a given grapheme/phoneme pair are matched up in our
            pool of readings and reading variants.
        """
        if len(grapheme) == 1:
            phoneme = scripts.toHiragana(phoneme)
            readings = self._pool.get(grapheme, [])
            return phoneme in readings
        else:
            return False

    #------------------------------------------------------------------------#

    def _parseKanjiDics(self, filenames):
        """ Parses kanjidic for on and kun readings, and okurigana.
        """
        readings = {}
        readingPool = {}
        okuri = {}

        for filename in filenames:
            print '----> Parsing reading information from %s' % `filename` 
            iStream = sopen(filename, 'r')

            for line in iStream:
                if line.startswith('#'):
                    # ignore comment lines
                    continue
    
                result = self._parseEntry(line)
                kanji, potentialReadings, potentialOkuri = result
    
                if potentialOkuri:
                    # not all kanji form okurigana stems
                    okuri[kanji] = potentialOkuri
    
                readings[kanji] = potentialReadings
    
                # add pooled readings for quick checking
                pooledReadings = set()
                for reading, readingLoc, readingType in potentialReadings:
                    pooledReadings.add(reading)
    
                rendakuExtras = filter(None, map(alternations.rendakuVariants,
                        pooledReadings))
                pooledReadings = pooledReadings.union(flatten(rendakuExtras))
    
                onbinExtras = filter(None, map(alternations.onbinVariants,
                        pooledReadings))
                pooledReadings = pooledReadings.union(flatten(onbinExtras))
    
                readingPool[kanji] = pooledReadings

            iStream.close()

        return readings, readingPool, okuri

    #------------------------------------------------------------------------#
    
    def _parseEntry(self, line):
        """ Parses a single line from kanjidic.
        """
        katakana = scripts.Script.Katakana
        hiragana = scripts.Script.Hiragana

        line = line.split()
        kanji, rest = line[0], line[1:]

        readings = set()
        okurigana = set()
        for item in rest:
            if item == 'T2' or item.startswith('{'):
                # lets not include radical names or their english meanings
                break

            # determine the location this reading is used
            if item.startswith('-'):
                location = ReadingLoc.prefix
                reading = item[1:]
            elif item.endswith('-'):
                location = ReadingLoc.prefix
                reading = item[:-1]
            else:
                location = ReadingLoc.any
                reading = item

            # deterime whether it is an on or kun reading
            readingScript = scripts.scriptType(reading)
            if readingScript == katakana:
                readingType = ReadingType.on
            elif readingScript == hiragana:
                readingType = ReadingType.kun
            else:
                # this is not an entry we want to keep
                continue

            reading = scripts.toHiragana(reading)

            if '.' in reading:
                # the reading is a case of okurigana
                reading, okuriEnding = reading.split('.')
                # XXX threw out location and reading
                okurigana.add(okuriEnding)

            readings.add((reading, location, readingType))

        return kanji, list(readings), list(okurigana)

    #------------------------------------------------------------------------#

    def _readSegments(self, segmentString):
        return tuple(segmentString.strip('|').split('|'))

    #------------------------------------------------------------------------#

    def __del__(self):
        """ Dumps the model upon leaving.
        """
        oStream = open(path.join(settings.DATA_DIR, 'readingModel.pickle'),
                'w')
        model = self._readings, self._pool, self._okuri
        pickle.dump(model, oStream)
        oStream.close()
        return

    #------------------------------------------------------------------------#

#----------------------------------------------------------------------------#
