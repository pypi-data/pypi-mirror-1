#!/usr/bin/env python
# -*- coding: utf-8 -*-
#----------------------------------------------------------------------------#
# formatEval.py
# Lars Yencken <lars.yencken@gmail.com>
# vim: ts=4 sw=4 sts=4 et tw=78:
# Wed Sep  7 16:10:02 EST 1005
#
#----------------------------------------------------------------------------#

import os, sys
import optparse
from cjktools.common import sopen

from entry import Entry

#----------------------------------------------------------------------------#

def formatEvalFile(inputFile, outputFile):
    entries = _parseEntries(inputFile)
    oStream = sopen(outputFile, 'w')

    for entry in entries:
        lineA = entry.gString.ljust(10, u'　')
        lineB = entry.pString.ljust(10, u'　')

        extraA, extraB = _matchAlignents(entry.alignments[0])
        lineA += extraA.ljust(10, u'　')
        lineB += extraB.ljust(10, u'　')

        extraA, extraB = _matchAlignents(entry.alignments[1])
        lineA += extraA.ljust(10, u'　')
        lineB += extraB.ljust(10, u'　')

        print >> oStream, lineA
        print >> oStream, lineB
        print >> oStream

    oStream.close()

    return

#----------------------------------------------------------------------------#

def _matchAlignents(alignment):
    gSegments, pSegments = map(list, alignment)
    for i in range(len(gSegments)):
        lenDiff = len(pSegments[i]) - len(gSegments[i])
        gSegments[i] = gSegments[i].ljust(len(pSegments[i]), u'　')

    lineA = u'｜'.join(gSegments)
    lineB = u'｜'.join(pSegments)

    return lineA, lineB

#----------------------------------------------------------------------------#

def _parseEntries(inputFile):
    entries = []
    for line in sopen(inputFile, 'r'):
        base, attempt, actual = line.strip().split(':')

        gString, pString = base.split()
        entry = Entry(gString, pString)
        fixify = lambda x: map(lambda y: y.strip('|').split('|'), 
                x.split())
        attempt = fixify(attempt)
        actual = fixify(actual)

        entry.alignments=[attempt, actual]
        
        entries.append(entry)

    return entries

#----------------------------------------------------------------------------#

def createOptionParser():
    """ Creates an option parser instance to handle command-line options.
    """
    usage = "%prog [options] inputFile outputFile"

    parser = optparse.OptionParser(usage)

    return parser

#----------------------------------------------------------------------------#

def main(argv):
    """ The main method for this module.
    """

    parser = createOptionParser()
    (options, args) = parser.parse_args(argv)

    try:
        [inputFile, outputFile] = args
    except:
        parser.print_help()
        sys.exit(1)

    # execute new code here
    formatEvalFile(inputFile, outputFile)
    
    return

#----------------------------------------------------------------------------#

if __name__ == '__main__':
    main(sys.argv[1:])

#----------------------------------------------------------------------------#

# vim: ts=4 sw=4 sts=4 et tw=78:
