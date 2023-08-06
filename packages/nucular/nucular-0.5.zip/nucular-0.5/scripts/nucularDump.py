#!/usr/bin/python

"""
Dump nucular entries to xml specification
"""

usage = """
NUCULARDUMP USAGE:

*** Dump a nucular archive to files

% python nucularDump.py --prefix fileNamePrefix archivePath

Dump the entries from the archive at archivePath to xml
file fileNamePrefix0.xml.  If there are more than 1000 entries
the second 1000 will go in fileNamePrefix1.xml, the third
will go in fileNamePrefix2.xml and so forth.  The data files
can be used to recreate the archive using the nucularLoad script.

Rationale for using many files:
large data sets are broken into multiple files
so they can be reloaded into an archive without difficulty
in multiple stages.

*** Dump a nucular archive using specified chunk size

% python nucularDump.py --chunkSize 10000 --prefix fileNamePrefix archivePath

The above specifies that up to 10000 entries should go in each
generated file (rather than the default of 1000).

*** Dump silently

% python nucularDump.py --silent --prefix fileNamePrefix archivePath

the "--silent" option suppresses verbose progress reporting to
standard output.
"""

from nucular import Nucular
from nucular import getparm
#from nucular import entry
#from nucular.findetree import etree
import os
import sys

def go():
    args = sys.argv[1:]
    silent = getparm.getparm(args, "--silent", default=False, getValue=False)
    prefix = getparm.getparm(args, "--prefix")
    if not prefix:
        raise ValueError, "please specify '--prefix FILENAMEPREFIX' for file dump"
    chunkSizeString = getparm.getparm(args, "--chunkSize", default="1000")
    gotChunks = False
    try:
        chunkSize = int(chunkSizeString)
        gotChunks = True
    finally:
        if not gotChunks:
            print "could not convert chunkSize to integer "+repr(chunkSizeString)
    if len(args)!=1:
        raise ValueError, "bad arguments (expect archiveLocation) "+repr(args)
    if chunkSize<1:
        raise ValueError, "chunksize must be positive "+repr(chunkSize)
    archiveLocation = args[0]
    verbose = not silent
    filecount = 0
    entrycount = 0
    entryInFileCount = 0
    file = None
    if verbose:
        print "opening archive", archiveLocation
    N = Nucular.Nucular(archiveLocation)
    currentId = N.firstId()
    while currentId:
        entrycount += 1
        if not file or entryInFileCount>=chunkSize:
            if file:
                if verbose:
                    print "closing file"
                file.write("\n</entries>\n")
                file.close()
            # open a new file with current count
            filename = "%s%s.xml" % (prefix, filecount)
            if verbose:
                print "opening file", filename
            file = open(filename, "w")
            file.write("<entries>\n")
            filecount += 1
            entryInFileCount = 0
        file.write("\n")
        thisEntry = N.describe(currentId)
        thisXML = thisEntry.toXML()
        file.write(thisXML)
        entryInFileCount += 1
        currentId = N.nextId(currentId)
    if file:
        if verbose:
            print "closing file", file
        file.write("\n</entries>\n")
        file.close()
    if verbose:
        print "finished dumping", entrycount, "entries"
            
if __name__=="__main__":
    complete = False
    try:
        go()
        #print parseXMLText(ExampleXML)
        complete = True
    finally:
        if not complete:
            print usage


