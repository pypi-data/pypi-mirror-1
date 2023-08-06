# -*- coding: utf-8 -*-
#----------------------------------------------------------------------------#
# dictionary.py
# Lars Yencken <lars.yencken@gmail.com>
# vim: ts=4 sw=4 sts=4 et tw=78:
# Mon May 16 10:50:57 EST 2005
#
#----------------------------------------------------------------------------#

""" This module is responsible for parsing input data sets for
    grapheme/phoneme string pairs to align. Its main methods are
    edictEntries() and evaluationEntries().
"""

#----------------------------------------------------------------------------#

from os import path

from cjktools import scripts
from cjktools.common import sopen

from entry import Entry
import settings

#----------------------------------------------------------------------------#
# PUBLIC METHODS
#

def edictEntries(inputFile):
    """ Determines all the kanji entries available in the input file. The input
        file is assumed to be in edict format.
    """
    inputStream = sopen(inputFile)
    rejectionStream = sopen(path.join(settings.LOG_DIR, 'rejected-entries'),
            'w')

    entries = []
    numRejected = 0
    for line in inputStream:
        lineParts = line.split()
        gString = lineParts[0]
        pString = lineParts[1][1:-1]
        
        if _validEntry(gString, pString):
            entries.append(Entry(gString, pString))
        else:
            numRejected += 1
            rejectionStream.write(line)

    return entries, numRejected

#----------------------------------------------------------------------------#

def evaluationEntries(inputFile):
    """ Get entries from a file formatted like an evaluation type instead of
        in edict format.
    """
    entries = []
    inputStream = sopen(inputFile, 'r')

    rejectionStream = sopen(path.join(settings.LOG_DIR, 'rejected-entries'),
            'w')

    numRejected = 0
    for line in inputStream:
        gString, pString = line.split(':')[0].split()
        
        if _validEntry(gString, pString):
            entries.append(Entry(gString, pString))
        else:
            numRejected += 1
            rejectionStream.write(line)

    return entries, numRejected

#----------------------------------------------------------------------------#

def separateEntries(entries, maxRunLength=3):
    """ Split out the longest entries for later processing.
    """
    shortEntries = []
    longEntries = []

    for entry in entries:
        if _longestKanjiRun(entry.gString) > maxRunLength:
            longEntries.append(entry)
        else:
            shortEntries.append(entry)
    
    return shortEntries, longEntries

#----------------------------------------------------------------------------#

#----------------------------------------------------------------------------#
# PRIVATE METHODS
#

def _validEntry(gString, pString):
    """ Returns True if the word is only kanji and kana, False otherwise.
    """
    # throw out any grapheme string which contains ascii
    if scripts.Script.Ascii in map(scripts.scriptType, gString): 
        return False

    # throw out any reading which non-kana readings
    isKana = lambda x: x in (scripts.Script.Hiragana, scripts.Script.Katakana)

    hasNonKana = (filter(isKana, map(scripts.scriptType, pString)) != [])

    return hasNonKana
    
#----------------------------------------------------------------------------#

def _longestKanjiRun(gString):
    """ Works out the longest number of kanji in a row in the grapheme string.
    """
    run = 0
    longest = 0
    kanjiScript = scripts.Script.Kanji
    for char in gString:
        if scripts.scriptType(char) == kanjiScript:
            run += 1
        else:
            if run > longest:
                longest = run
            run = 0
    else:
        if run > longest:
            longest = run
    
    return longest

#----------------------------------------------------------------------------#
