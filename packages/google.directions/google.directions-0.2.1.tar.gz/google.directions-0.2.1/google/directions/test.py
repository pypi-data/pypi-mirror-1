#!/usr/bin/env python

from gdapi import GoogleDirections

import os, re, sys, getopt

class Usage(Exception):
    def __init__(self, msg):
        self.msg = msg

def main(argv=None):
    if argv is None:
        argv = sys.argv
    try:
        try:
            opts, args = getopt.getopt(argv[1:], "h", ["help"])
        except getopt.error, msg:
            raise Usage(msg)

        try:
            key = args[0]
            start = args[1]
            destination = args[2]
        except IndexError:
            raise Usage("Didn't specify key, start and destination.")

    except Usage, err:
        print >>sys.stderr, err.msg
        print >>sys.stderr, "Usage: test.py <key> <start> <destination>"
        return 1



    """
    Code here!
    """

    res = GoogleDirections(key).query(start,destination)

    if res.status != 200:
        print "Address not found. Status was: %d" % res.status
        return 1

    print "Distance: %dm" % res.distance


if __name__ == "__main__":
    sys.exit(main())

