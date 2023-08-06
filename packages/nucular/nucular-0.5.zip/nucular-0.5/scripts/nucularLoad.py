#!/usr/bin/python

"""
Load nucular entries from xml specification
"""

usage = """
NUCULARLOAD USAGE:

*** Load entries from an XML file to archive with deferred visibility

% python nucularLoad.py --xml fileName.xml archivePath

Load the entries in fileName.xml (encoded as xml) into the
nucular archive at archivePath.  The updates will not be
visible until the next time the archive is aggregated.
By default if any duplicate identities are found between
the new entries and the existing archive entries, the load
will be aborted.

*** Load entries from standard input XML to archive with deferred visibility

% python nucularLoad.py --stdin archivePath

Loads the entries from standard input (encoded as xml).
The updates will not be
visible until the next time the archive is aggregated.

*** Load entries with immediate visibility

By default the entries will be inserted in "deferred" mode,
meaning they will not be visible until the archive is aggregated.
To make the entries visible to queries immediately add the
"--visible" flag.

% python nucularLoad.py --visible --xml fileName.xml archivePath

Warning: if too many updates are made visible immediately
before aggregation accesses to the archive may become slower.

*** Load entries and aggregate the archive immediately

To automatically aggregate recent updates for the archive
following the inserts add the --aggregate flag

% python nucularLoad.py --aggregate --xml fileName.xml archivePath

If the archive is large this may take some time to complete.

*** Load silently

To suppress verbose progress messages to standard output add
the "--silent" flag.

% python nucularLoad.py --silent --xml fileName.xml archivePath

*** Load and replace duplicate identities

To replace existing entries that match on id use --replace

% python nucularLoad.py --replace --xml fileName.xml archivePath

*** Delete entries

To delete existing entries that match on id from input (and not replace them)
use --delete.

% python nucularLoad.py --delete --xml fileName.xml archivePath

*** Give example XML

Use the "--exampleXML" flag to get a sample of the xml format
required for encoding entries printed to standard output.

% python nucularLoad.py --exampleXML

"""

# XXX this KISS implementation is not appropriate for very large XML files.

ExampleXML = """
<!--
Note: The top level tag is the "entries" which contains "entry" elements.
-->
<entries>

    <!-- entry elements must have a unique id and any number of fld attribute definitions -->
    <entry id="CA">
        <!-- fld names are given by the (required) "n" attribute -->
        <!-- fld values are the string content of the fld element -->
        <!-- an entry may have several fld elements with the same name -->
        <fld n="category">U.S. State</fld>
        <fld n="name">Republic of California</fld>
        <fld n="nickname">The Golden State</fld>
        <fld n="nickname">Disney World State</fld>
    </entry>
    
    <!-- the entries do not need to have the same attributes, except for the required "id" -->
    <entry id="T2T">
        <fld n="Title">Tale of Two Cities</fld>
        <fld n="Author">Charles Dickens</fld>
    </entry>

    <entry id="DEC">
        <fld n="Company">Digital Equipment</fld>
        <fld n="Business">Computer hardware, parts and services</fld>
        <fld n="Status">Now part of Compaq</fld>
    </entry>
</entries>

"""

from nucular import Nucular
from nucular import getparm
from nucular import entry
from nucular.findetree import etree
import os
import sys

def go():
    args = sys.argv[1:]
    if args==["--exampleXML"]:
        print ExampleXML
        return
    silent = getparm.getparm(args, "--silent", default=False, getValue=False)
    visible = getparm.getparm(args, "--visible", default=False, getValue=False)
    delete = getparm.getparm(args, "--delete", default=False, getValue=False)
    replace = getparm.getparm(args, "--replace", default=False, getValue=False)
    aggregate = getparm.getparm(args, "--aggregate", default=False, getValue=False)
    stdin = getparm.getparm(args, "--stdin", default=False, getValue=False)
    xmlFileName = getparm.getparm(args, "--xml")
    if delete and replace:
        raise ValueError, "cannot both delete and replace (it doesn't make sense)"
    if not xmlFileName or stdin:
        raise ValueError, "please specify --xml FILENAME or --stdin"
    if len(args)!=1:
        raise ValueError, "bad arguments (expect archiveLocation) "+repr(args)
    archiveLocation = args[0]
    verbose = not silent
    if verbose:
        print "now parsing input"
    if stdin:
        inputFile = sys.stdin
    else:
        inputFile = file(xmlFileName)
    Entries = parseXML(inputFile)
    if verbose:
        print "now loading input into archive", archiveLocation
    N = Nucular.Nucular(archiveLocation)
    addedCount = 0
    removeCount = 0
    for e in Entries:
        identity = e.identity()
        if N.hasIdentity(identity):
            if delete or replace:
                if verbose:
                    print "removing existing entry for "+repr(identity)
                N.remove(identity)
                removeCount += 1
            else:
                raise ValueError, "found existing matching entry for id=%s: aborting" % repr(identity)
    if not delete:
        for e in Entries:
            if verbose:
                print "adding", e
            N.index(e)
            addedCount += 1
    lazy = (not visible)
    if verbose:
        print "now storing data, lazy=", lazy
    N.store(lazy=lazy)
    if aggregate:
        if verbose:
            print "aggregating archive"
            N.aggregateRecent(fast=True, verbose=verbose)
            N.moveTransientToBase(verbose=verbose)
            N.cleanUp()
    else:
        if verbose:
            print
            print "WARNING: NOT AGGREGATING ARCHIVE!"
            if lazy:
                print "  CHANGES WILL NOT BE VISIBLE UNTIL ARCHIVE HAS BEEN AGGREGATED."
            print
    if verbose:
        print
        print "load complete: removed", removeCount, "and added", addedCount

def parseXML(inputFile):
    text = inputFile.read() # XXX what if it's too big?
    return entry.EntriesFromXMLText(text)

# functionality moved to entry module
# def parseXMLText(text):
#     result = {}
#     tree = etree.fromstring(text) # XXX what if it's too big?
#     if tree.tag!="entries":
#         raise ValueError, "failed to find top level tag 'entries' in XML"
#     for elt in tree.getchildren():
#         thisEntry = entry.EntryFromXMLNode(elt)
#         if thisEntry is not None:
#             identity = thisEntry.identity()
#             if result.has_key(identity):
#                 raise ValueError, "repeated identity is not permitted "+repr(identity)
#             result[identity] = thisEntry
#     if not result:
#         raise ValueError, "no entry elements found in XML"
#    return result.values()
    
if __name__=="__main__":
    complete = False
    try:
        go()
        #print parseXMLText(ExampleXML)
        complete = True
    finally:
        if not complete:
            print usage
