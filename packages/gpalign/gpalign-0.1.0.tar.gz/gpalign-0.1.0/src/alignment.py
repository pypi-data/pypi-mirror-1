# -*- coding: utf-8 -*-
#----------------------------------------------------------------------------#
# alignment.py
# Lars Yencken <lars.yencken@gmail.com>
# vim: ts=4 sw=4 sts=4 et tw=78:
# Mon May 16 11:24:31 EST 2005
#
#----------------------------------------------------------------------------#

""" This module implements the iterative TF-IDF method.
"""

#----------------------------------------------------------------------------#

import potentials
from frequency import FrequencyMap

from cjktools import scripts
from cjktools.common import sopen
from consoleLog.progressBar import ProgressBar

import math
import random
import cPickle as pickle

#----------------------------------------------------------------------------#

# epsilon for testing for zero
eps = 1e-8

#----------------------------------------------------------------------------#

class AlignmentModel:
    """ This class is responsible for the alignment algorithm, and all its
        internal data structures.
    """
    #------------------------------------------------------------------------#
    # PUBLIC METHODS
    #

    def __init__(self, outputFile, options):
        """ Creates a new instance using the list of correctly aligned
            readings.
        """
        print 'Initialising alignment model'
        if options.modelInput:
            print '--> Seeding from', `options.modelInput`
            self._uniqueCounts = pickle.load(open(options.modelInput))
        else:
            print '--> Seeding from empty model'
            self._uniqueCounts = FrequencyMap()

        self._ambiguousCounts = FrequencyMap()

        # possibly a filename to dump our final model into
        self._modelDumpFile = options.modelOutput

        # whether to align all at once or iteratively
        self._iterative = options.iterative

        # we write aligned readings as we go, rather than storing them in
        # memory
        self._output = sopen(outputFile, 'w')
        self._outputName = outputFile

        # ratios for the tf-idf
        self._alpha = options.alpha
        self._solved = options.solved
        self._unsolved = options.unsolved

        # setting either of these defaults non-zero will prevent calculation
        # of that heuristic
        if options.random:
            self._useRandom = True
            print '--> Random model selected'
        else:
            self._useRandom = False

            # only define these variables in the non-random case to ensure
            # that they never get used in the random case
            self._defaultTf = 0
            self._defaultIdf = 0
    
            if not options.tfHeuristic:
                print '--> Disabling tf heuristic'
                self._defaultTf = 1
    
            elif not options.idfHeuristic:
                print '--> Disabling idf heuristic'
                self._defaultIdf = 1
            
            else:
                print '--> Full TF-IDF enabled'

        return
    
    #------------------------------------------------------------------------#

    def addResolved(self, resolvedEntries):
        """ Populates the statistical model with a number of resolved entries. 
        """
        # add all unambiguous readings to our model
        for entry in resolvedEntries:
            self._uniqueCounts.addCounts(entry.alignment)
            print >> self._output, entry.toLine()

        return

    #------------------------------------------------------------------------#

    def disambiguate(self, ambiguous):
        """ Incorporates and aligns the ambiguous readings based on existing
            alignments.
        """
        if not ambiguous:
            return

        self._initialiseEntries(ambiguous)
        numEntries = len(ambiguous)

        if self._useRandom:
            # randomly pick the best alignment for each entry
            self._randomAlignment(ambiguous)

        elif not self._iterative:
            # perform first and only scoring iteration
            self._rescore(ambiguous)
    
        progressBar = ProgressBar()
        progressBar.start(100)

        i = 0
        while i < numEntries:
            if self._iterative and not self._useRandom:
                # perform expensive rescoring
                self._rescore(ambiguous)
                ambiguous.sort()

            bestEntry = ambiguous.pop()
            self._disambiguateEntry(bestEntry)

            print >> self._output, bestEntry.toLine()

            i += 1
            progressBar.fractional(math.sqrt(i)/math.sqrt(numEntries))

        progressBar.finish()

        return

    #------------------------------------------------------------------------#
    
    def finish(self):
        """ Closes the output stream and sorts the output for easier
            comparison.
        """
        self._output.close()

        if self._modelDumpFile:
            # dump our 
            oStream = open(self._modelDumpFile, 'w')
            pickle.dump(self._uniqueCounts, oStream)
            oStream.close()

        assert self._ambiguousCounts._gSize == 0

        return
    
    #------------------------------------------------------------------------#

    #------------------------------------------------------------------------#
    # PRIVATE METHODS
    #

    def _initialiseEntries(self, ambiguousEntries):
        """ Updates the counts for ambiguous readings and restructures them to
            be updated.
        """
        for i in xrange(len(ambiguousEntries)):
            entry = ambiguousEntries[i]
            alignments = entry.potentials

            assert len(set(alignments)) == len(alignments), \
                    "Readings are not unique"

            # update our counts
            for alignment in alignments:
                self._ambiguousCounts.addCounts(alignment)

            entry.score = 0.0
            entry.scores = [0.0]*len(alignments)

        return
 
    #------------------------------------------------------------------------#

    def _disambiguateEntry(self, entry):
        """ Modify the entry to remove all the additional ambiguous alignments,
            and update our internal counts.
        """
        entry.scores = None

        # put this count amongst the unique ones
        self._uniqueCounts.addCounts(entry.alignment)

        # fill in the rest of this count
        # eliminate the bad readings from the model
        for alignment in entry.potentials:
            self._ambiguousCounts.delCounts(alignment)

        entry.potentials = None
        entry.aligned = True

        return

    #------------------------------------------------------------------------#

    def _rescore(self, ambiguous):
        """ Loops over the entire list of ambiguous entries, rescoring each.
        """
        for i in xrange(len(ambiguous)):
            entry = ambiguous[i]

            entry.scores = map(self._tfidf, entry.potentials)
            entry.score, entry.alignment = max(zip(entry.scores, \
                    entry.potentials))

        return

    #------------------------------------------------------------------------#

    def _weightedFreqs(self, gSegments, pSegments, index):
        """ Weight the frequencies from the two models.
        """
        s_gFreq, s_gpFreq, s_gpcFreq = self._uniqueCounts.frequencies(
                gSegments, pSegments, index)
        u_gFreq, u_gpFreq, u_gpcFreq = self._ambiguousCounts.frequencies(
                gSegments, pSegments, index)

        gFreq = self._solved*s_gFreq + self._unsolved*u_gFreq
        gpFreq = self._solved*s_gpFreq + self._unsolved*u_gpFreq
        gpcFreq = self._solved*s_gpcFreq + self._unsolved*u_gpcFreq

        return gFreq, gpFreq, gpcFreq
        
    #------------------------------------------------------------------------#

    def _explainAlignment(self, entry, alignment):
        """
        """
        bestScore, allAlignments = entry
        print '--->', bestScore,
        potentials.printAlignment(alignment)
        allAlignments.sort()
        allAlignments.reverse()
        for otherScore, otherAlignment in allAlignments:
            print '----->', otherScore,
            potentials.printAlignment(otherAlignment)
    
        return

    #------------------------------------------------------------------------#

    def _randomAlignment(self, entries):
        """ Picks a random alignment for each entry in a list of ambiguous
            entries. 
        """
        for ambiguousEntry in entries:
            ambiguousEntry.alignment = random.sample(
                    ambiguousEntry.potentials, 1)[0]
        return

    #------------------------------------------------------------------------#

    def _tfidf(self, alignment):
        """ Calculates the tf-idf score of the alignment passed in based on
            the current model.
        """
        kanjiScript = scripts.Script.Kanji
        currentScores = []

        gSegments, pSegments = alignment
        for i in range(len(gSegments)):
            if not scripts.scriptType(gSegments[i]) == kanjiScript:
                continue

            gFreq, gpFreq, gpcFreq = self._weightedFreqs(gSegments,
                    pSegments, i)

            tf = self._defaultTf or \
                (gpFreq + self._alpha - self._unsolved) / gFreq

            idf = self._defaultIdf or \
                math.log(gpFreq/(gpcFreq + self._alpha - self._unsolved))

            currentScores.append(tf*idf)
 
        newScore = sum(currentScores) / float(len(currentScores))

        return newScore

    #------------------------------------------------------------------------#

#----------------------------------------------------------------------------#

