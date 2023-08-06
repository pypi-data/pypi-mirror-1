#!/usr/bin/env python
from texttools.guesslang import guessfilelang
from optparse import OptionParser

if __name__ == '__main__':
    usage = "usage: %prog file"
    parser = OptionParser()
    options, args = parser.parse_args()
    if len(args) != 1:
        parser.error("incorrect number of arguments")

    similarities = guessfilelang(*args)
    print(similarities[0][1])

