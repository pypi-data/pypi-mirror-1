#!/usr/bin/env python
# -*- coding: utf-8 -*-
#----------------------------------------------------------------------------#
# detectOkurigana.py
# Lars Yencken <lars.yencken@gmail.com>
# vim: ts=4 sw=4 sts=4 et tw=78:
# Sat May 14 14:49:45 EST 2005
#
#----------------------------------------------------------------------------#

""" This module is an executable script performing grapheme-phoneme alignment
    based on papers by Baldwin and Tanaka.
"""

#----------------------------------------------------------------------------#

import os, sys
import optparse

import potentials
import dictionary
from alignment import AlignmentModel
from readingModel import ReadingModel
from okuriganaModel import OkuriganaModel
import evaluate
import settings

#----------------------------------------------------------------------------#

def detectOkurigana(outputFile, options):
    """ Performs just okurigana detection and alignment alteration.
    """
    okuriganaModel = OkuriganaModel(options)

    inputFile = options.inputFile or os.path.join(settings.DATA_DIR,
            'eval-okurigana.data')
    okuriganaModel.okuriganaAdjustments(inputFile, outputFile)

    if not options.inputFile:
        evaluate.evaluateOkurigana(outputFile, outputFile + '.eval')

    return

#----------------------------------------------------------------------------#


#----------------------------------------------------------------------------#
# COMMAND-LINE INTERFACE
#

def createOptionParser():
    """ Creates an option parser instance to handle command-line options.
    """
    usage = \
"""%prog [options] outputFile

An efficient implementation of the Baldwin-Tanaka automated grapheme-phoneme
alignment algorithm based on TF-IDF."""

    parser = optparse.OptionParser(usage)

    parser.add_option('-t', '--threshold', action='store',
            dest='okuriThreshold', type='int', default=1,
            help='The threshold used for cooccurrence-based okurigana')

    parser.add_option('--simple', action='store_true',
            dest='simpleOkurigana', default=False,
            help='Use a simple okurigana method, ignoring the main model')

    parser.add_option('--no-kanjidic', action='store_false',
            dest='useKanjidic', default=True,
            help='Disables the kanjidic reading model')

    parser.add_option('--no-cooccurrence', action='store_false',
            dest='useCooccurrence', default=True,
            help='Disables cooccurrence entries from edict')

    parser.add_option('--no-verbs', action='store_false',
            dest='useVerbs', default=True,
            help='Disables verb entries from edict')

    parser.add_option('-i', '--input', action='store', dest='inputFile',
            help="Specify a custom input file to use.")

    return parser

#----------------------------------------------------------------------------#

def main(argv):
    """ The main method for this module.
    """
    parser = createOptionParser()
    (options, args) = parser.parse_args(argv)

    if len(args) != 1:
        parser.print_help()
        sys.exit(1)

    outputFile = args[0]

    detectOkurigana(outputFile, options)

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

