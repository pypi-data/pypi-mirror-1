# -*- coding: utf-8 -*-
#----------------------------------------------------------------------------#
# frequency.py
# Lars Yencken <lars.yencken@gmail.com>
# vim: ts=4 sw=4 sts=4 et tw=78:
# Thu Aug 11 16:01:52 EST 2005
#
#----------------------------------------------------------------------------#

from cjktools import scripts

#----------------------------------------------------------------------------#

class FrequencyMap:
    """ The data structure within which frequency counts for tf-idf
        calculations are stored.
    """
    def __init__(self):
        self._graphemes = {}

        self._gSize = 0.0
        self._gpSize = 0.0
        self._gpcSize = 0.0

        return
    
    def addCounts(self, alignment):
        """ This method updates all the counts associated with the entry.
        """
        kanjiScript = scripts.Script.Kanji
        gSegments, pSegments = alignment
        for i in range(len(gSegments)):
            if scripts.scriptType(gSegments[i]) == kanjiScript:
                g, gp, gpc = self._getContext(gSegments, pSegments, i)

                if not self._graphemes.has_key(g):
                    # if we don't have g, we can't have gp, gpc
                    self._graphemes[g] = (1, {gp: (1, {gpc: 1})})
                    self._gSize += 1
                    self._gpSize += 1
                    self._gpcSize += 1

                else:
                    gCount, gpDict = self._graphemes[g]
                    gCount += 1
                    if not gpDict.has_key(gp):
                        # without gp, we also can't have gpc
                        gpDict[gp] = (1, {gpc: 1})
                        self._gpSize += 1
                        self._gpcSize += 1
                    else:
                        gpCount, gpcDict = gpDict[gp]
                        gpCount += 1
                        if not gpcDict.has_key(gpc):
                            gpcDict[gpc] = 1
                            self._gpcSize += 1
                        else:
                            gpcDict[gpc] += 1
                        gpDict[gp] = gpCount, gpcDict
                    self._graphemes[g] = gCount, gpDict

        return
    
    def delCounts(self, alignment):
        """ This method updates all the counts associated with the entry.
        """
        kanjiScript = scripts.Script.Kanji
        gSegments, pSegments = alignment
        for i in range(len(gSegments)):
            if scripts.scriptType(gSegments[i]) == kanjiScript:
                g, gp, gpc = self._getContext(gSegments, pSegments, i)
                gCount, gpDict = self._graphemes[g]
                gCount -= 1
                if gCount < 1:
                    del self._graphemes[g]
                    self._gSize -= 1
                    continue

                gpCount, gpcDict = gpDict[gp]
                gpCount -= 1
                if gpCount < 1:
                    del gpDict[gp]
                    self._gpSize -= 1
                    self._graphemes[g] = gCount, gpDict
                    continue

                gpcCount = gpcDict[gpc]
                gpcCount -= 1
                if gpcCount < 1:
                    del gpcDict[gpc]
                    self._gpcSize -= 1
                else:
                    gpcDict[gpc] = gpcCount

                gpDict[gp] = gpCount, gpcDict
                self._graphemes[g] = gCount, gpDict

        return
        
    def _getContext(self, gSegments, pSegments, index):
        """ Determine the context needed for calculations or for frequency
            updates.
        """
        grapheme = gSegments[index]
        phoneme = pSegments[index]

        # determine the left context...
        if index > 0:
            leftG = gSegments[index-1]
            leftP = pSegments[index-1]
        else:
            leftG = None
            leftP = None

        # ...and the right context 
        if index < len(gSegments) - 1:
            rightG = gSegments[index+1]
            rightP = pSegments[index+1]
        else:
            rightG = None
            rightP = None

        return grapheme, phoneme, (leftG, leftP, rightG, rightP)
    
    def frequencies(self, gSegments, pSegments, index):
        """ Calculates the frequencies of occurence of the segment specified
            within the alignment.
        """
        g, gp, gpc = self._getContext(gSegments, pSegments, index)

        gFreq, gpDict = self._graphemes.get(g, (0, {}))
        gpFreq, gpcDict = gpDict.get(gp, (0, {}))
        gpcFreq = gpcDict.get(gpc, 0)

        gFreq /= self._gSize
        gpFreq /= self._gpSize
        gpcFreq /= self._gpcSize

        return gFreq, gpFreq, gpcFreq
    
#----------------------------------------------------------------------------#
