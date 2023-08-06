#!/usr/bin/python

"""
Aggregate a nucular archive.
"""

usage = """
NUCULARAGGREGATE USAGE

"nucularAggregate.py" performs maintenance operations
which optimize an updated nucular archive structure.
Aggregations are only needed after multiple update
operations.

*** Aggregate recent operations to intermediate storage

% python nucularAggregate.py archivePath

Aggregate the recent updates to the archive into the
"Transient" tree.  This will make "deferred" updates
visible and possibly make archive accesses faster.

*** Aggregate in fast mode

% python nucularAggregate.py --fast archivePath

Perform the aggregation using the "fast" protocol
(which consumes more memory but runs faster than the
default protocol when enough real memory is available).
If there are too many updates memory thrashing may
ensue (causing slowness) or memory may be exhausted
(causing a MemoryError after a very long wait).  If
this happens don't use --fast next time.

*** Full aggregation

% python nucularAggregate.py --full archivePath

Aggregate recent updates to the transient tree and
then merge the transient tree with the base archive.
This should be done less frequently than the partial
aggregation and may take a long time for large data
sets.

*** Silent aggregation

% python nucularAggregate.py --silent archivePath

Perform the aggregation without verbose progress reports
to standard output.

The --full, --fast, and --silent flags may be combined.
"""

# XXX for the moment leaving out the "target" feature

from nucular import Nucular
from nucular import getparm
import os
import sys

def go():
    args = sys.argv[1:]
    silent = getparm.getparm(args, "--silent", default=False, getValue=False)
    fast = getparm.getparm(args, "--fast", default=False, getValue=False)
    full = getparm.getparm(args, "--full", default=False, getValue=False)
    verbose = not silent
    if len(args)!=1:
        raise ValueError, "bad arguments (expect archiveLocation) "+repr(args)
    archiveLocation = args[0]
    if verbose:
        print "getting archive", archiveLocation
    N = Nucular.Nucular(archiveLocation)
    if verbose:
        print "aggregating recent updates, fast=", fast
    N.aggregateRecent(fast=fast, verbose=verbose)
    if full:
        if verbose:
            print "combining transient and base archives"
        N.moveTransientToBase(verbose=verbose)
    if verbose:
        print "unlinking retired files"
    N.cleanUp()
    print "aggregation complete"

if __name__=="__main__":
    complete = False
    try:
        go()
        #print parseXMLText(ExampleXML)
        complete = True
    finally:
        if not complete:
            print usage
