 #!/usr/bin/python

"""
Query a nucular archive (script)
"""

usage = """
NUCULARQUERY USAGE:

*** Evaluate an XML Query using an archive

% python nucularQuery.py --xml queryFileName.xml archivePath

Prints the result of evaluating queryFileName to standard output
as an XML entries dump.  By default XML comments are added providing
additional verbose information.

*** Find entries from an archive where a field starts with a given prefix

% python nucularQuery.py --prefix name:value archivePath

Prints a dump of entries where field "name" has "value" as a prefix.

*** Find entries from an archive where a field contains a given word prefix

% python nucularQuery.py --contains name:word archivePath

Prints a dump of entries where field "name" contains a
word with "word" as a prefix.

*** Find entries from an archive where any field contains a given word prefix (free text search)

% python nucularQuery.py --contains word archivePath

Prints a dump of entries where any field contains has some word
with "word" as a prefix,

*** Find entries from an archive where a field lies in a specified range

% python nucularQuery.py --range name:aaalow..zzzhigh archivePath

Print dump of entries where the field "name" has a value between
aaalow and zzzhigh (in string ordering).

*** Find entries from an archive where has a specified value

% python nucularQuery.py --match name=value archivePath

Print dump of entries where the field "name" has the value "value"

*** Find proximate words in any field

% python nucularQuery.py --near 3:words..near..eachother archivePath

Print dump or entries in the archive where some field
contains the words "words" and "near" and "eachother" in
that order separated by no more than 3 intervening words.

The --prefix, --contains, --near, and --range flags may be provided multiple
times and combined.  Only one --xml flag is allowed.

*** Print suggested field values

% python nucularQuery.py --match name=value --suggestions archivePath

The --suggestions flag instructs the script to print a sequence of
suggestions for values for the fields of the database selected
from entries in the query result.

*** Suppress comments

% python nucularQuery.py --match name=value --silent archivePath

The --silent flag will suppress verbose XML comments in the output.

*** Print Example XML

% python nucularQuery.py --exampleXML

Prints an example for the XML query format to standard output
"""

ExampleXML = """
<!-- example XML for query specification -->

<query>

    <!-- social security number must start with 787 -->
    <prefix n="socialSecurityNumber" p="787"/>

    <!-- age should be between 09 (inclusive) and 45 (exclusive) in string order -->
    <range n="age" low="09" high="45"/>

    <!-- interests contains word programming -->
    <contains n="interests" p="programming"/>

    <!-- interests also contains word horses -->
    <contains n="interests" p="horses"/>

    <!-- the word "java" occurs in some attribute value as a prefix -->
    <contains p="java"/>

    <!-- the gender must match "female" -->
    <match n="gender" v="female"/>

    <!-- the words "swing dancing" must occur in that order somewhere
         separated by no more than 3 intervening words -->
    <near words="swing dancing" limit="3"/>

</query>
"""

suggestionsExample = """
% python nucularQuery.py --contains bysshe ../testdata/gutenberg/ --suggestions
<!-- archive= ../testdata/gutenberg/
<query threaded="False">
   <contains p="bysshe"/>
</query>
-->
<suggestions>
    <suggest>
         bysshe shelley
    </suggest>
    <suggest n="Author">
         wtctlxxx
         thomas
         xxx
         pbs
         xenophon
         ptbllxxx
         hutchinson
         thompson
         dmntwxxx
         shelley
         bysshe
         sotheran
    </suggest>
    <suggest n="Commentator">
         frederickson
    </suggest>
    <suggest n="Comments">
         edward
         thomas
         note
         translator
         poetical
         author
         bysshe
         hutchinson
         about
         percy
         frederickson
         editor
         alex
         works
         iii
         bedrijven
    </suggest>
    <suggest n="Contains">
         4797
         4799
    </suggest>
    <suggest n="Editor">
         morley
    </suggest>
    <suggest n="Language">
         dutch
    </suggest>
    <suggest n="Subtitle">
         essay
         vier
         bedrijven
    </suggest>
    <suggest n="Title">
         and
         daemon
         works
         symonds
         third
         bell
         reformer
         john
         bysshe
         philosopher
         percy
         socrates
         addington
         witch
         ontboeid
         atlas
         world
         the
         shelley
         thoughts
    </suggest>
    <suggest n="Tr.">
         bysshe
    </suggest>
    <suggest n="Translator">
         gutteling
    </suggest>
    <suggest n="i">
         4800
         16872
         4555
         4695
         4697
         17490
         4696
         1336
         4654
         4798
         4799
         4797
         17822
    </suggest>
    <suggest n="link">
    </suggest>
</suggestions>

 """
    
from nucular import Nucular
from nucular import getparm
from nucular import entry
import os
import sys

def go():
    args = sys.argv[1:]
    if args==["--exampleXML"]:
        print ExampleXML
        return
    silent = getparm.getparm(args, "--silent", default=False, getValue=False)
    suggestions = getparm.getparm(args, "--suggestions", default=False, getValue=False)
    verbose = not silent
    xmlFileName = getparm.getparm(args, "--xml")
    prefixD = {}
    containsD = {}
    rangeD = {}
    matchD = {}
    nearD = {}
    while "--prefix" in args:
        prefixspec = getparm.getparm(args, "--prefix")
        if ":" not in prefixspec:
            raise ValueError, "prefix specification must be of form name:value "+repr(prefixspec)
        (name, value) = prefixspec.split(":",1)
        prefixD[(name,value)] = 1
    while "--range" in args:
        rangespec = getparm.getparm(args, "--range")
        if ":" not in rangespec:
            raise ValueError, "range specification must be of form name:low..high "+repr(rangespec)
        (name,lowhigh) = rangespec.split(":", 1)
        lowhighSplit = lowhigh.split("..", 1)
        if len(lowhighSplit)!=2:
            raise ValueError, "range specification must be of form name:low..high "+repr(rangespec)
        (low, high) = lowhighSplit
        rangeD[ (name, low, high) ] = 1
    while "--contains" in args:
        containsspec = getparm.getparm(args, "--contains")
        if ":" in containsspec:
            (name, value) = containsspec.split(":", 1)
            containsD[ (name, value) ] = 1
        else:
            containsD[ (None, containsspec) ] = 1
    while "--match" in args:
        matchspec = getparm.getparm(args, "--match")
        if "=" not in matchspec:
            raise ValueError, "match specification must be of form name=value "+repr(matchspec)
        (name, value) = matchspec.split("=", 2)
        matchD[ (name, value) ] = 1
    while "--near" in args:
        ok = False
        nearspec = getparm.getparm(args, "--near")
        if ":" in nearspec:
            csplit = nearspec.split(":")
            if len(csplit)==2:
                (slimit, words) = csplit
                try:
                    limit = int(slimit)
                except:
                    print "failed integer conversion: "+repr(limit)
                else:
                    swords = words.split("..")
                    print words, "split to", swords
                    nearD[ (limit, tuple(swords)) ] = 1
                    ok = True
        if not ok:
            raise ValueError, "near specification must be of form '--near 3:words..near..eachother "+repr(nearspec)
    if len(args)!=1:
        raise ValueError, "bad arguments (expect archiveLocation) "+repr(args)
    archiveLocation = args[0]
    N = Nucular.Nucular(archiveLocation)
    if xmlFileName:
        text = file(xmlFileName).read()
        Q = N.QueryFromXMLText(text)
    else:
        Q = N.Query()
    for (limit, words) in nearD:
        Q.proximateWords(words, limit)
    for (name,value) in matchD:
        Q.matchAttribute(name, value)
    for (name,value) in prefixD:
        Q.prefixAttribute(name, value)
    for (name, high, low) in rangeD:
        Q.attributeRange(name, high, low)
    for (name, value) in containsD:
        if name is None:
            Q.anyWord(value)
        else:
            Q.attributeWord(name, value)
    if verbose:
        print "<!-- archive=", archiveLocation
        print Q.toXML()
        print "-->"
    if suggestions:
        # print suggestions, not query result
        (L, D) = Q.suggestions()
        print "<suggestions>"
        if L:
            print "    <suggest>"
            for x in L:
                print "        ", x
            print '    </suggest>'
        items = D.items()
        items.sort()
        for (attr, values) in items:
            print '    <suggest n="%s">'%attr
            for v in values:
                print "        ", v
            print '    </suggest>'
        print "</suggestions>"
        return
    # no evaluation limit
    (result, status) = Q.evaluate(maxBufferLimit=10e15)
    if verbose:
        print "<!-- result status=", status, "-->"
        print
    if result:
        print result.toXML()
        if verbose:
            print
            print "<!-- ", result.size(), "entries in result set -->"
    else:
        print "<!-- no result returned: evaluation failed -->"

if __name__=="__main__":
    complete = False
    try:
        go()
        complete = True
    finally:
        if not complete:
            print usage
