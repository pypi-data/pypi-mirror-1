#!/usr/bin/env python
# -*- coding: utf-8 -*-
#----------------------------------------------------------------------------#
# align.py
# Lars Yencken <lars.yencken@gmail.com>
# vim: ts=4 sw=4 sts=4 et tw=78:
# Sat May 14 14:49:45 EST 2005
#
#----------------------------------------------------------------------------#

""" This module performs pure segmentation and alignment only.
"""

#----------------------------------------------------------------------------#

import os, sys
import optparse
import pdb
from cjktools.common import sopen

from gpalign import potentials
from gpalign import dictionary
from gpalign.alignment import AlignmentModel
from gpalign.readingModel import ReadingModel
from gpalign.okuriganaModel import OkuriganaModel
from gpalign import evaluate

#----------------------------------------------------------------------------#

def performSegmentation(inputFile, outputFile, options):
    """ The main method for this module. Performs the entire segmentation run,
        taking an edict dictionary as input and producing a segmented output
        for each kanji input row.
    """
    # read in edict dictionary
    if not options.edict:
        print 'Reading evaluation entries'
        entries, numRejected = dictionary.evaluationEntries(inputFile)
    else:
        print 'Reading edict entries'
        entries, numRejected = dictionary.edictEntries(inputFile)

    print '--> Found %d entries (rejected %d)' % (len(entries), numRejected)

    print 'Separating long and short entries'
    shortEntries, longEntries = dictionary.separateEntries(entries,
            options.longestRun)
    print '--> %d short, %d long' % (len(shortEntries), len(longEntries))

    alignmentModel = AlignmentModel(outputFile, options)

    if options.useKanjidic:
        readingModel = ReadingModel()
        kanjidicOkurigana = readingModel.getOkurigana()
    else:
        readingModel = None
        kanjidicOkurigana = {}

    print 'PASS 1: SHORT ENTRIES'
    _resolveEntries(alignmentModel, readingModel, shortEntries, options)
    del shortEntries

    print 'PASS 2: LONG ENTRIES'
    _resolveEntries(alignmentModel, readingModel, longEntries, options)
    del longEntries

    del readingModel

    alignmentModel.finish()
    del alignmentModel

    if not options.edict:
        evaluate.evaluateAlignment(outputFile, outputFile + '.eval')

    return

#----------------------------------------------------------------------------#

def _resolveEntries(model, readingModel, entries, options):
    """ 
    """
    print 'Generating possible alignments'
    unique, ambiguous = potentials.generateAlignments(entries, options)
    print '--> %d unique, %d ambiguous' % (len(unique), len(ambiguous))
    print '--> %d overconstrained' % \
            (len(entries) - (len(unique) + len(ambiguous)))

    if options.useKanjidic:
        print 'Disambiguating using kanjidic'
        moreUnique, ambiguous = readingModel.pruneAlignments(ambiguous)
        print '--> %d unique, %d ambiguous' % (len(moreUnique), len(ambiguous))
        unique.extend(moreUnique); del moreUnique

    print 'Disambiguating readings using statistical model'
    print '--> Processing %d unique entries' % len(unique)
    model.addResolved(unique); del unique
    print '--> Beginning statistical disambiguation of %d entries' % \
            len(ambiguous)
    model.disambiguate(ambiguous); del ambiguous

    return

#----------------------------------------------------------------------------#


#----------------------------------------------------------------------------#
# COMMAND-LINE INTERFACE
#

def createOptionParser():
    """ Creates an option parser instance to handle command-line options.
    """
    usage = \
"""%prog [options] inputFile outputFile

An efficient implementation of the Baldwin-Tanaka automated grapheme-phoneme
alignment algorithm based on TF-IDF. By default, it uses an evaluation data set
as input, and prints an accuracy analysis for the score."""

    parser = optparse.OptionParser(usage)

    parser.add_option('--max-per-kanji', action='store', dest='maxPerKanji',
            type='int', default=5,
            help='The maximum number of kana aligned to one kanji [5]')

    parser.add_option('--no-kanjidic', action='store_false',
            dest='useKanjidic', default=True,
            help='Disables the kanjidic reading model')

    parser.add_option('--idf-only', action='store_false', dest='tfHeuristic',
            default=True, help='Only uses the idf heuristic [False]')

    parser.add_option('--tf-only', action='store_false', dest='idfHeuristic',
            default=True, help='Only uses the tf heuristic [False]')

    parser.add_option('--random', action='store_true', dest='random',
            help='Choose a random entry to disambiguate each time [False]')

    parser.add_option('--longest-run', action='store', dest='longestRun',
            type='int', default=4,
            help='The longest kanji run to be handled in the first pass [4]')

    parser.add_option('--edict', action='store_true',
            dest='edict', help='Use the EDICT dictionary as input [False]')

    parser.add_option('-a', '--alpha', action='store', dest='alpha',
            default=2.5, type='float',
            help='The smoothing value to use in tf-idf [2.5]')

    parser.add_option('-s', '--solved', action='store', dest='solved',
            default=0.07, type='float',
            help='The weight of solved frequencies in the tf-idf equation [0.07]')

    parser.add_option('-m', '--max-potentials', action='store',
            dest='maxPotentials', type='int', default=120,
            help='The maximum number of potential alignments for an entry [120]')

    parser.add_option('--non-iterative', action='store_false',
            dest='iterative', default=True,
            help='Disables iterative alignment, instead taking one pass [False]')
    parser.add_option('-u', '--unsolved', action='store', dest='unsolved',
            default=0.13, type='float',
            help='The weight of unsolved frequencies in the tf-idf equation [0.13]')

    parser.add_option('--dump-model', action='store', dest='modelOutput',
            help="At the end of alignment, dump the model " + \
            "generated to the given file.")

    parser.add_option('--use-model', action='store', dest='modelInput',
            help="Instead of generating a model, use this one.")

    return parser

#----------------------------------------------------------------------------#

def main(argv):
    """ The main method for this module.
    """
    parser = createOptionParser()
    (options, args) = parser.parse_args(argv)

    if len(args) != 2:
        parser.print_help()
        sys.exit(1)

    inputFile, outputFile = args

    if options.random:
        options.tfHeuristic = False
        options.idfHeuristic = False

    performSegmentation(inputFile, outputFile, options)

    return

#----------------------------------------------------------------------------#

if __name__ == '__main__':
    try:
        import psyco
        psyco.profile()
    except:
        pass

    try:
        main(sys.argv[1:])
    except KeyboardInterrupt:
        # we cancel runs often, so do it nicely
        print >> sys.stderr, '\nAborting run!'
        sys.exit(1)

#----------------------------------------------------------------------------#

