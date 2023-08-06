#!/usr/bin/env python
# -*- coding: utf-8 -*-
#----------------------------------------------------------------------------#
# evaluate.py
# Lars Yencken <lars.yencken@gmail.com>
# vim: ts=4 sw=4 sts=4 et tw=78:
# Fri Aug 12 11:41:18 EST 2005
#
#----------------------------------------------------------------------------#

import os, sys
import optparse

from cjktools import sequences
from cjktools.common import sopen

import errors
import settings

#----------------------------------------------------------------------------#

def evaluateAlignment(predictionFile, resultsFile):
    """ Evaluates the alignments provided in the prediction file, writing the
        results to the results file.
    """
    validationFile = os.path.join(settings.DATA_DIR, 'eval-alignment.data')

    iStream = sopen(predictionFile, 'r')
    results = {}

    validationCases = _listEntries(validationFile)
    validationDict = dict(validationCases)

    predictionCases = _listEntries(predictionFile)
    predictionDict = dict(predictionCases)

    matching = lambda x: x in validationCases
    good, bad = sequences.separate(matching, predictionCases)

    results['good'] = good

    addCorrect = lambda x: x + (validationDict[x[0]],)
    bad = map(addCorrect, bad)

    results['bad'] = bad

    orFunc = lambda x, y: x or y
    hasGapping = lambda x: reduce(orFunc, map(lambda y: '<' in y, x[2]))
    gapping, align = sequences.separate(hasGapping, bad)

    results['gapping'] = gapping
    results['align'] = align

    isMissing = lambda x: not predictionDict.has_key(x[0])
    missing = filter(isMissing, validationCases)
    results['missing'] = missing

    _writeResults(results, resultsFile)

    return

#----------------------------------------------------------------------------#

def evaluateOkurigana(predictionFile, resultsFile):
    """ Evaluates the alignments provided in the prediction file, writing the
        results to the results file.
    """
    validationFile = os.path.join(settings.DATA_DIR, 'eval-okurigana.data')

    iStream = sopen(predictionFile, 'r')
    results = {}

    validationCases = _listEntries(validationFile)
    validationDict = dict(validationCases)

    predictionCases = _listEntries(predictionFile)
    predictionDict = dict(predictionCases)

    matching = lambda x: x in validationCases
    good, bad = sequences.separate(matching, predictionCases)

    results['good'] = good

    addCorrect = lambda x: x + (validationDict[x[0]],)
    bad = map(addCorrect, bad)

    results['okuri'] = bad

    isMissing = lambda x: not predictionDict.has_key(x[0])
    missing = filter(isMissing, validationCases)
    results['missing'] = missing

    results['bad'] = bad + missing

    _writeResults(results, resultsFile)

    return

#----------------------------------------------------------------------------#

def _writeResults(resultsDict, resultsFile):
    keys = resultsDict.keys()
    keys.sort()

    summaryStream = open(resultsFile, 'w')

    for key in keys:
        keyEntries = resultsDict[key]
        number = len(keyEntries)
        percent = 100.0*number/5000.0
        print >> summaryStream, '%s    %4d    %6.2f%%' % (key, number, percent)
        print '%s    %4d    %6.2f%%' % (key, number, percent)
        oStream = sopen(resultsFile + '.' + key, 'w')
        for line in keyEntries:
            print >> oStream, ':'.join(line)
        oStream.close()

    return

#----------------------------------------------------------------------------#


def _listEntries(filename):
    entries = []
    iStream = sopen(filename, 'r')

    for line in iStream:
        key, value = line.strip().split(':', 1)
        entries.append((key, value))

    iStream.close()

    return entries

#----------------------------------------------------------------------------#

def evaluate(predictionFile, validationFile, validationResults):
    """ Evaluates the predictions against the validation data, writing the
        output to a series of files with basename validationResults.
    """
    testEntries = _getEntries(predictionFile)
    correctEntries = _getEntries(validationFile)

    _compareEntries(testEntries, correctEntries, validationResults)

    # split the errors into a detailed analysis
    errors.separateErrors(validationResults)

    return

#----------------------------------------------------------------------------#

def _getEntries(filename):
    """ Creates a dictionary of all the entries in the given file.
    """
    lines = sopen(filename, 'r').readlines()

    entries = {}
    for line in lines:
        key, value = line.split(':')[:2]
        entries[key] = value.strip()

    return entries

#----------------------------------------------------------------------------#

def _compareEntries(testEntries, correctEntries, resultFile):
    """ Compares the entries from the different files.
    """
    nLines = 0
    nCorrect = 0
    nMissing = 0
    oStream = sopen(resultFile, 'w')
    for key, alignment in correctEntries.iteritems():
        testAlignment = testEntries.get(key, '???')

        if alignment == testAlignment:
            nCorrect += 1

        if testAlignment == '???':
            nMissing += 1

        print >> oStream, '%s:%s:%s' % (key, testAlignment, alignment)

        nLines += 1
    
    oStream.close()

    print 'Got %.2f%% correct!' % (nCorrect*100.0/nLines)
    if nMissing > 0:
        print '   but %d were missing...' % nMissing

    return

#----------------------------------------------------------------------------#

def sortFile(filename):
    """ Sorts the file in a line-based manner.
    """
    iStream = sopen(filename, 'r')
    lines = iStream.readlines()
    iStream.close()

    lines.sort()

    oStream = sopen(filename, 'w')
    oStream.writelines(lines)
    oStream.close()

    return

#----------------------------------------------------------------------------#

def createOptionParser():
    """ Creates an option parser instance to handle command-line options.
    """
    usage = "%prog [options] rawResults adjustedResults"

    parser = optparse.OptionParser(usage)

    
    parser.add_option('-e', action='store', dest='correctFile',
        default=os.path.join(settings.DATA_DIR, 'evaluation.data'),
        help='The file of correct evaluations')

    return parser

#----------------------------------------------------------------------------#

def main(argv):
    """ The main method for this module.
    """
    parser = createOptionParser()
    (options, args) = parser.parse_args(argv)

    try:
        [testOutputFile, resultsFile] = args
    except:
        parser.print_help()
        sys.exit(1)

    # execute new code here
    evaluate(testOutputFile, options.correctFile, resultsFile)
    
    return

#----------------------------------------------------------------------------#

if __name__ == '__main__':
    main(sys.argv[1:])

#----------------------------------------------------------------------------#

# vim: ts=4 sw=4 sts=4 et tw=78:
