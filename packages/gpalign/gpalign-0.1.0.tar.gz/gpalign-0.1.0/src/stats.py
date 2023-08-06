# -*- coding: utf-8 -*-
#----------------------------------------------------------------------------#
# stats.py
# Lars Yencken <lars.yencken@gmail.com>
# vim: ts=4 sw=4 sts=4 et tw=78:
# Mon May 16 14:18:59 EST 2005
#
#----------------------------------------------------------------------------#

""" This module is responsible for any general combinatoric methods, in
    particular determining possible combinations of input.
"""

#----------------------------------------------------------------------------#
# PUBLIC METHODS
#

def combinations(combinationList):
    """ Generates a list of all possible combinations of one element from the
        first item in combinationList, one from the second, etc. For example::

            > combinations([[1, 2], ['dog'], ['a', 'b']])
            [[1, 'dog', 'a'], [2, 'dog', 'a'], [1, 'dog', 'b'], 
            [2, 'dog', 'b']]
    """
    combinationList = combinationList[:]
    combinationList.reverse()

    combos = map(lambda x: (x,), combinationList.pop())

    while combinationList:
        nextLevelCombos = []
        for itemToAdd in combinationList.pop():
            # add this item to the end of every existing combo 
            for existingCombo in combos:
                nextLevelCombos.append(existingCombo + (itemToAdd,))

        combos = nextLevelCombos

    return combos

#----------------------------------------------------------------------------#

def combinationTuples(combinationList):
    """ Generates a list of all possible combinations of one element from the
        first item in combinationList, one from the second, etc. For example::

            > combinations([[1, 2], ['dog'], ['a', 'b']])
            [[1, 'dog', 'a'], [2, 'dog', 'a'], [1, 'dog', 'b'], 
            [2, 'dog', 'b']]
    """
    combinationList = combinationList[:]
    combinationList.reverse()

    combos = combinationList.pop()

    while combinationList:
        nextLevelCombos = []
        for itemToAdd in combinationList.pop():
            # add this item to the end of every existing combo 
            for existingCombo in combos:
                nextLevelCombos.append(existingCombo + itemToAdd)

        combos = nextLevelCombos

    return combos

#----------------------------------------------------------------------------#

def segmentCombinations(gString):   
    """ Determines the possible segment combinations based on the grapheme
        string alone, in particular due to kanji placement. For example::

            > segmentCombinations('学校')
            [(学,校),(学校)]
        
    """
    # start out with just the first character
    segmentations = [[gString[0]]]

    # add remaining characters one by one
    for char in gString[1:]: 
        nextSegmentationRound = []
        for segment in segmentations:
            # the new char in its own segment
            nextSegmentationRound.append(segment + [char])

            # the new char as part of the previous segment
            segment[-1] += char
            nextSegmentationRound.append(segment)

        segmentations = nextSegmentationRound
    
    segmentations = map(tuple, segmentations)

    return segmentations

#----------------------------------------------------------------------------#

#----------------------------------------------------------------------------#
# PRIVATE METHODS
#

#----------------------------------------------------------------------------#
