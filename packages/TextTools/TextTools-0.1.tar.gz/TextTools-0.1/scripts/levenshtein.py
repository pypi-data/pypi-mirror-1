#!/usr/bin/env python
from texttools import levenshtein
from optparse import OptionParser

if __name__ == '__main__':
    usage = "usage: %prog file1 file2"
    parser = OptionParser()
    options, args = parser.parse_args()
    if len(args) != 2:
        parser.error("incorrect number of arguments")

    distance, ratio = levenshtein.files_distance(*args)
    if distance == 0:
        print('Same content!')
    else:
        print('%.2f%% similar' % ratio)

