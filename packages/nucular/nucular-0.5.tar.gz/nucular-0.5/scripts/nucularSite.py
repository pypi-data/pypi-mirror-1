#!/usr/bin/python

"""
Create a new nucular archive ( or recreate an old one)
"""

usage = """
NUCULARSITE USAGE

*** Create a new nucular archive

% python nucularSite.py directory

  Create the directory and initialize an empty nucular archive structure there.

*** Erase and re-create a nucular archive

% python nucularSite.py --reset directory

  If the directory exists, erase it's content and replace it with an empty
  nucular archive structure.

  Adding a "--silent" flag will suppress debug prints
"""

import shutil
import sys
import os
from nucular import Nucular

def go():
    args = sys.argv[1:]
    reset = False
    verbose = True
    if "--reset" in args:
        reset = True
        args.remove("--reset")
    if "--silent" in args:
        verbose = False
        args.remove("--silent")
    if len(args)!=1:
        print "I don't understand the arguments", args
        print "I am looking for a single directory path"
        print usage
        return
    directory = args[0]
    if reset:
        #cmd = "rm -rf %s" % directory
        if verbose:
            print "--reset specified: deleting", directory
        shutil.rmtree(directory)
    if verbose:
        print "creating directory", directory
    os.mkdir(directory)
    if verbose:
        print "installing nucular archive in", directory
    N = Nucular.Nucular(directory)
    N.create()
    if verbose:
        print "creation complete"

if __name__=="__main__":
    complete = False
    try:
        go()
        complete = True
    finally:
        if not complete:
            print "creation failed"
            print
            print usage



