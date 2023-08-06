# -*- coding: utf-8 -*-
#----------------------------------------------------------------------------#
# entry.py
# Lars Yencken <lars.yencken@gmail.com>
# vim: ts=4 sw=4 sts=4 et tw=78:
# Thu Aug 25 15:28:58 EST 2005
#
#----------------------------------------------------------------------------#

from cjktools import scripts

#----------------------------------------------------------------------------#

class Entry:
    """ A single grapheme-phoneme pair undergoing alignment.
    """
    def __init__(self, gString, pString):
        """ Creates a new instance.

            @param gString: The grapheme string
            @param pString: The phoneme string
            @param potentials: Potential alignments pre-calculated
            @param score: The current scoring
        """
        self.pString = pString
        self.gString_original = gString

        # normalise the graphical form
        if u'々' in gString:
            gString = self._insertDuplicateKanji(gString)
        self.gString = gString

        # have we aligned yet?
        self.aligned = False

        # best alignment so far and its score
        self.score = None
        self.alignment = None

        # potential alignments and their scores
        self.potentials = None
        self.scores = None

        return

    def __cmp__(self, otherEntry):
        return cmp(self.score, otherEntry.score)

    def toString(self):
        if self.aligned:
            gSegments, pSegments = self.alignment
            retStr = 'Entry(%s <-> %s)' % \
                    ('|'.join(gSegments), '|'.join(pSegments))
        elif self.potentials:
            retStr = 'Entry(%s <-> %s, %d potentials)' % \
                    (self.gString, self.pString, len(self.potentials))
        else:
            retStr = 'Entry(%s <-> %s)' % (self.gString, self.pString)
        return retStr

    def __str__(self):
        return self.toString()
    
    def __repr__(self):
        return self.toString()

    def toLine(self):
        """ Prints the final alignment in our desired output format. 
        """
        assert self.aligned

        alignment = ' '.join(map(lambda x: '|'.join(x), self.alignment))

        original = '%s %s'%(self.gString_original, ''.join(self.alignment[1]))
    
        return ':'.join((original, alignment))

    def _insertDuplicateKanji(self, gString):
        result = []
        kanjiScript = scripts.Script.Kanji
        for i, c in enumerate(gString):
            if c == u'々' and i > 0 and scripts.scriptType(gString[i-1]) == kanjiScript:
                # Insert a duplicate of the previous kanji
                result.append(gString[i-1])
            else:
                result.append(c)

        return ''.join(result)

    def __hash__(self):
        if not self.alignment:
            return hash(self.gString + self.pString)
        else:
            return hash(tuple(self.alignment))
    
#----------------------------------------------------------------------------#
