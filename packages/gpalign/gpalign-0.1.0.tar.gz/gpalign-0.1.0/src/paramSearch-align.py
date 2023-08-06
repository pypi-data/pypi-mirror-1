#!/usr/bin/env python
# -*- coding: utf-8 -*-
#----------------------------------------------------------------------------#
# scriptedRun.py
# Lars Yencken <lars.yencken@gmail.com>
# vim: ts=4 sw=4 sts=4 et tw=78:
# Mon Sep 12 15:09:37 EST 2005
#
#----------------------------------------------------------------------------#

import re
import os, sys
import csv
import pdb
import warnings

warnings.filterwarnings("ignore")

from sequences import frange
import stats

argv = sys.argv[1:]

if len(argv) < 1:
    print >> sys.stderr, 'Usage: ./scriptedRun.py output.csv [extra args]'
    sys.exit(1)

outputFile = argv[0]
argString = ' '.join(argv[1:])

totalGood = re.compile('good[     ]+([0-9]+)[     ]+')

alphaRange = frange(0.1, 2.1, 0.2)
sRange = frange(0.1, 3.1, 0.2)
uRange = frange(0.1, 3.1, 0.2)

dataFile = csv.writer(open(outputFile, 'w'))
tmpDir = os.tempnam('/tmp', 'param')
os.mkdir(tmpDir)
outputFile = os.path.join(tmpDir, 'align.out')

header = ('alpha', 's', 'u', 'good')
dataFile.writerow(header)
header += ('best',)
line = '%10s %10s %10s %10s %10s' % header
print line
print '-'*(len(line)+4)

best = 0
for alpha, s, u in stats.combinations([alphaRange, sRange, uRange]):
    if alpha > min(u, s) or u > s:
        continue

    print '%10.2f %10.1f %10.1f' % (alpha, s, u), 
    sys.stdout.flush()
    command = './align.py %s -a %f -s %f -u %f %s' % \
            (argString, alpha, s, u, outputFile)
    iStream = os.popen(command)
    data = iStream.read()

    nGood = totalGood.search(data)
    if nGood is None:
        print
        print 'Having trouble with command:'
        print command
        sys.exit(1)
    else:
        nGood = int(nGood.group(1))

    if nGood > best:
        best = nGood
        print '%10d %10.2f (*)' % (nGood, best/50.0)
    else:
        print '%10d %10.2f' % (nGood, best/50.0)

    dataFile.writerow((alpha, s, u, nGood))

# vim: ts=4 sw=4 sts=4 et tw=78:
