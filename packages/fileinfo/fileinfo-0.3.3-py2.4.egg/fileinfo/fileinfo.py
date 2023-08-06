#!/usr/bin/env python
# _*_ coding: UTF-8 _*_

"""Investigate and present file attributes in a tabular fashion.

"""

import re, sys, glob, getopt, os, os.path, operator
from os.path import join, basename, dirname, splitext, commonprefix
from os.path import isdir, isabs, abspath, normpath, exists
from pprint import pprint as pp

from compatibility import *
from utils import groupby
import investigator
import plugging


__version__ = "0.3.3"
__license__ = "GNU General Public Licence v3 (GPLv3)"
__author__ = "Dinu Gherman"
__date__ = "2008-11-14"


ATTR_SEP = ":"
OS_ENVIRON_PLUGIN_VARNAME = "FILEINFO_PLUGIN_PATH"
INVESTIGATOR_CLASSES = []


def loadPlugins():
    "Load investigator plugins."
    
    plugins = []
    
    # load builtin plugins, if present
    plugins += plugging.getPluginsFromModule(investigator, 
        investigator.BaseInvestigator)
    
    # load additional plugins, if present
    plugins += plugging.loadPlugins(
        investigator.BaseInvestigator, 
        "fileinfo_inv_plugin_*.py", 
        folder=join(dirname(abspath(__file__)), "plugins"),
        envVar=OS_ENVIRON_PLUGIN_VARNAME
    )
    
    return plugins


class FileAttrRecord:
    "A record for collecting file attributes."
    
    pass
    

# Code below this point is meant for command-line usage.

def _showVersion():
    "Print version message."

    prog = basename(sys.argv[0])
    print "%s %s" % (prog, __version__)
    sys.exit()


def _showPlugins():
    "List available plug-ins."

    for C in INVESTIGATOR_CLASSES:
        print C.__name__
    sys.exit()


def _runTests():
    "Run self-tests."

    import unittest
    from test import test_fileinfo
    suite = unittest.findTestCases(test_fileinfo)
    unittest.TextTestRunner().run(suite)
    sys.exit()


def _showUsage():
    "Print usage message."

    prog = basename(sys.argv[0])
    args = (prog, __version__, __author__, __date__[:4], __license__)
    print "%s v. %s, Copyleft by %s, %s (%s)" % args 
    print "Licensed under %s" % __license__
    print "Investigate and present file attributes in a tabular fashion."
    print "USAGE: %s [options [values]] file1 [file2 ...]" % prog
    print "OPTIONS:"
    print '  -h --help          Prints this usage message and exits.'
    print '     --help-attrs    Prints available attributes and exits.'
    print '     --list-plugins  Lists available plug-ins and exits.'
    print '  -v --version       Prints version number and exits.'
    print '  -t --test          Performs self-test and exits.'
    print '  -p --path MODE     Display path as abs, rel or base (default).'
    print '     --format MODE   Display result in formats simple (default),'
    print '                     csv, rest-simple, html or'
    print '                     cocoa or wx (experimental GUI frontends).'
    print '  -a --attrs NAME    Calculate attribute(s) of a file.'
    print '  -s --sort NAME     Sort output (asc.) by given attribute(s).'
    print '  -f --filters EXPR  Filter files that satisfy EXPR'
    print '                     (prefix filter attrs. with "rec.").'
    print "EXAMPLES:"
    print '  %s /my/files/*' % prog
    print '  %s /my/files/document.pdf' % prog
    print '  %s document.pdf' % prog
    print '  %s -a size:wc:lc *.txt' % prog
    print '  %s -a size -a size -f "rec.size < 1000" *.txt' % prog
    print '  %s -a size $(find . -name "*.py")' % prog
    print '  %s -a kMDItemISOSpeed:kMDItemExposureTimeSeconds *.jpg' % prog
    print "FURTHER EXAMPLES (EXPERIMENTAL GUIS):"
    print '  %s -a size:ndef --format cocoa *.py' % prog
    print '  %s -a size:ndef --format wx *.py' % prog
    sys.exit()


def _showHelpAttributes():
    "Print list of available attributes."

    # print "VALUES FOR -a, --attrs and -s, --sort:"
    print "Available attributes for options -a, --attrs and -s, --sort:"
    for C in INVESTIGATOR_CLASSES:
        print "%s:" % C.__name__
        items = C.attrMap.items()
        items.sort()
        for attrName, funcName in items:
            desc = C("dummy").getFunc(attrName).__doc__
            print '  %-19s%s' % (attrName, desc)
    sys.exit()


def _transpose(rows):
    "Convert a sequence of rows into a sequence of columns."
    
    r = rows
    cols = [[r[y][x] for y in range(len(r))] for x in range(len(r[0]))]
    # cols = [[rows[y][x] for y, row in enumerate(rows)] for x, col in enumerate(rows[y])] #:fix:#
    return cols
    

def getOptionValues(optDict, names):
    "Return list of unique values for several keys, split by some char."

    vals = []
    for optName in names:
        vals += optDict.get(optName, "").split(ATTR_SEP)
    vals = [a for a in vals if len(a) > 0]

    # remove duplicate entries while maintaining list order
    vls = []
    for v in vals:
        if v not in vls:
            vls.append(v)
    
    return vls


def rmCwdFromPath(path):
    "Return 'path' with removed common prefix from current working dir."
    
    common = commonprefix([os.getcwd(), path])
    if len(common) == 0:
        return path
    else:
        return path[len(common)+1:]


def getPaths(*pathPatterns):
    "Return a list of file paths described by 'pathPatterns'."
    
    pathLists = []
    for pp in pathPatterns:
        # pp = normpath(pp)
        if not isdir(pp):
            pathLists.append(pp)
        else:
            # pathLists.append(join(pp, "*"))
            pathLists.append(pp)
    # or in Python 2.5: #:fix:#
    # pathLists = [pp if not isdir(pp) else join(pp, "*") for pp in pathPatterns]
    pathLists = [glob.glob(pp) for pp in pathLists]
    paths = reduce(operator.add, pathLists, [])   

    return paths
    

def _collectAttrs(paths, options):
    "Collect attributes for all files."

    fileAttrRecs = []
    for path in paths:
        if isdir(path):
            continue
        if not isabs(path):
            path = join(os.getcwd(), path)
        fis = [C(path) for C in INVESTIGATOR_CLASSES]
        for fi in fis:
            fi.activate()
        fis = [fi for fi in fis if fi.active]
        fileAttrRec = FileAttrRecord()
        attrVals = getOptionValues(options, ["a", "attrs"])
        for a in attrVals:
            vals = [fi.getAttr(a) for fi in fis if fi.getAttr(a) != None]
            if vals:
                setattr(fileAttrRec, a, vals[0])
            else:
                setattr(fileAttrRec, a, "n/a")
        fileAttrRec.path = path
        fileAttrRecs.append(fileAttrRec)
    
    return fileAttrRecs


def collectAttrs(paths, options):
    "Collect attributes for all files."

    ## cache = readCaches(paths)
    
    fileAttrRecs = []
    for path in paths:
        if not isabs(path):
            path = join(os.getcwd(), path)

        # create list of instatiated investigators
        fis = [C(path) for C in INVESTIGATOR_CLASSES]

        # get list of user-defined attribute values
        attrVals = getOptionValues(options, ["a", "attrs"])

        # filter file investigators to those who can handle these attrs       
        fis2 = []
        for a in attrVals:
            for fi in fis:
                if a in fi.attrMap.keys() and not fi in fis2:
                    fis2.append(fi)
                matches = [re.match(an, a) 
                    for an in fi.attrMap.keys() if re.match(an, a)]
                if matches and not fi in fis2:
                    fis2.append(fi)
        fis = fis2

        # activate these file investigators
        for fi in fis:
            fi.activate()

        fileAttrRec = FileAttrRecord()
        for a in attrVals:
            vals = [fi.getAttrValue(a) for fi in fis]
            vals = [v for v in vals if v != None]
            if vals:
                setattr(fileAttrRec, a, vals[0])
            else:
                setattr(fileAttrRec, a, "n/a")
        fileAttrRec.path = path
        fileAttrRecs.append(fileAttrRec)
        
    # pp([rec.__dict__ for rec in fileAttrRecs])

    ## writeCache(fileAttrRecs)

    return fileAttrRecs


def process(*pathPatterns, **options):
    "Print file info table for a set of files."

    paths = getPaths(*pathPatterns)
    
    # collect desired file attributes
    all = collectAttrs(paths, options)
    if len(all) == 0:
        return

    # apply filtering expressions
    filterVals = getOptionValues(options, ["f", "filters"])
    for f in filterVals:
        ## print "*** %s", geta
        all = [rec for rec in all if eval(f)]    
        
    # sort according to desired field(s)...
    sortVals = getOptionValues(options, ["s", "sort"])
    if sortVals:
        all_deco = [[getattr(rec, sv) for sv in sortVals] + [rec] 
            for rec in all]
        all_deco.sort()
        all = [entry[-1] for entry in all_deco]

    # recalculate counter attribute if present
    attrVals = getOptionValues(options, ["a", "attrs"])
    if "counter" in attrVals:
        for i, rec in enumerate(all):
            rec.counter = i
    
    # handle option -p | --path
    mode = options.get("p", None) or options.get("path", None)
    if mode == "abs":
        display = abspath
    elif mode == "rel":
        display = rmCwdFromPath
    elif mode == "hidden":
        display = lambda p: "<hidden>" + splitext(p)[1]
    else:
        display = basename
    rows = [
        [getattr(rec, a) for a in attrVals] + [display(rec.path)] 
            for rec in all
    ]

    if len(rows) > 1 and len(attrVals) > 0:
        if 0:
            # add totals of numeric field(s)...
            rec = FileAttrRecord()
            for a in attrVals:
                setattr(rec, a, "")
                cs = [C for C in INVESTIGATOR_CLASSES if a in C.totals]
                if cs:
                    setattr(rec, a, sum([getattr(r, a) 
                        for r in all if getattr(r, a) != "n/a"]))
            row = [getattr(rec, a) for a in attrVals] + ["total"] 
            rows.append(row)

        else:    
            # add totals of numeric field(s)...
            rec = FileAttrRecord()
            for a in attrVals:
                setattr(rec, a, "")
                cs = [C for C in INVESTIGATOR_CLASSES if a in C.totals]
                if cs:
                    setattr(rec, a, investigator.getSum(a, all))
            row = [getattr(rec, a) for a in attrVals] + ["total"] 
            rows.append(row)
    
        # add header line
        rec = FileAttrRecord()
        for a in attrVals:
            setattr(rec, a, a)
        rec.path = "path"
        row = [getattr(rec, a) for a in attrVals] + [rec.path] 
        rows.insert(0, row)
    
    return rows


def displayAsTable(rows):
    "Display result as table."

    import operator 
    if rows == None or len(rows) == 0:
        return
    cols = _transpose(rows)
    
    ## print "*** col 0", cols[0]
    maxColWidths = [max([len(str(c)) for c in col]) for col in cols]
    ## print "*** maxColWidths", maxColWidths
    if len(rows) == 1:
        isNumCols = [reduce(operator.__and__, 
            [type(c) in (int, long, float) or c=="n/a" for c in col]) 
                for col in cols]
    else:
        isNumCols = [reduce(operator.__and__, 
            [type(c) in (int, long, float) or c=="n/a" for c in col[1:-1]]) 
                for col in cols]
    signs = [{False: "-", True: ""}[b] for b in isNumCols]
    ## print "*** isNumCols", isNumCols
    ## format = "".join(["%%%ds  " % (w) for w in maxColWidths[:-1]]) + "%s"
    format = "".join(["%%%s%ds  " % (signs[i], maxColWidths[i]) for i in range(len(maxColWidths)-1)]) + "%s"
    ## print "*** format", format
    for row in rows:
        print format % tuple(row)


def displayAsRESTSimpleTable(rows):
    "Display result as simple ReST table."

    if rows == None or len(rows) == 0:
        return
    cols = _transpose(rows)
    maxColWidths = [max([len(str(c)) for c in col]) for col in cols]
    ## isNumCols = [reduce(operator.__and__, [type(c) in (int, long, float) or c=="n/a" for c in col[1:-1]]) for col in cols]
    if len(rows) == 1:
        isNumCols = [reduce(operator.__and__, 
            [type(c) in (int, long, float) or c=="n/a" for c in col]) 
                for col in cols]
    else:
        isNumCols = [reduce(operator.__and__, 
            [type(c) in (int, long, float) or c=="n/a" for c in col[1:-1]]) 
                for col in cols]
    signs = [{False: "-", True: ""}[b] for b in isNumCols]
    ## format = "".join(["%%%ds  " % (w) for w in maxColWidths[:-1]]) + "%s"
    format = "".join(["%%%s%ds  " % (signs[i], maxColWidths[i]) 
        for i in range(len(maxColWidths)-1)]) + "%s"
    print format % tuple(["="*m for m in maxColWidths])
    
    for i, row in enumerate(rows):
        print format % tuple(row)
        if i == 0:
            print format % tuple(["="*m for m in maxColWidths])
    if len(rows) > 1:
        print format % tuple(["="*m for m in maxColWidths])


def displayCSV(rows):
    "Display as a CSV table."

    if rows == None or len(rows) == 0:
        return

    for row in rows:
        line = ";".join([str(i) for i in row])
        print line


def displayAsHtml(rows):
    "Display as a HTML table."

    if rows == None or len(rows) == 0:
        return

    print "<table>"
    for row in rows:
        print "  <tr>"
        for col in row:
            print "    <td>%s</td>" % str(col)
        print "  </tr>"
    print "</table>"


def _main():
    "Handle command-line."

    global INVESTIGATOR_CLASSES
    INVESTIGATOR_CLASSES += loadPlugins()

    shortOpts = "hvta:s:p:f:"
    longOpts = "help format= help-attrs show-plugins version test "
    longOpts += "attrs= sort= filters= path="
    longOpts = longOpts.split()

    try:
        opts, args = getopt.getopt(sys.argv[1:], shortOpts, longOpts)
    except getopt.GetoptError:
        print "ERROR"
        _showUsage()

    # add default values        
    if "--format" not in [k for (k, v) in opts]:
        opts.append(("--format", "simple"))

    stopOptions = "-v --version -h --help --help-attrs -t --test --show-plugins"
    stopOptions = [k for (k, v) in opts if k in stopOptions]
    if len(args) == 0 and len(stopOptions) == 0:
        _showUsage()
    
    for k, v in opts:
        if k in ("-h", "--help"):
            _showUsage()
        elif k == "--help-attrs":
            _showHelpAttributes()
        elif k == "--show-plugins":
            _showPlugins()
        elif k in ("-v", "--version"):
            _showVersion()
        elif k in ("-t", "--test"):
            sys.argv.remove(k)
            _runTests()
        elif k in ("-p", "--path"):
            available = "base abs rel hidden".split()
            if v not in available:
                print "Error: Unknown path display mode: %s" % v
                print "Available names are:", ", ".join(available)
                sys.exit()            
        elif k == "--format":
            available = "csv simple rest-simple html cocoa wx django".split()
            if v not in available:
                print "Error: Unknown format display mode: %s" % v
                print "Available names are:", ", ".join(available)
                sys.exit()
        elif k in ("-a", "--attrs", "-s", "--sort"):
            at = reduce(operator.add, [C.attrMap.keys() 
                for C in INVESTIGATOR_CLASSES], [])
            matches = [re.match(an, v) for an in at if re.match(an, v) != None]
            diff = set(v.split(ATTR_SEP)) - set(at)
            if len(diff) > 0 and len(matches) == 0:
                args = ", ".join(list(diff))
                msg = "Error: Unknown file attribute name(s): %s" % args
                print msg
                print "Available names are:", ", ".join(at)
                sys.exit()
    
    optItems = [(k.lstrip("-"), v) for (k, v) in opts]
    optDict = dict(optItems)
    rows = process(*args, **optDict)
    
    format = optDict["format"]
    if format == "simple":
        displayAsTable(rows)
    elif format == "rest-simple":
        displayAsRESTSimpleTable(rows)
    elif format == "csv":
        displayCSV(rows)
    elif format == "html":
        displayAsHtml(rows)
    elif format == "cocoa":
        import guicocoa
        HEADER = rows[0]
        FOOTER = [rows[-1]]
        TABLE = rows[1:-1]
        guicocoa.main(HEADER, TABLE, FOOTER)
    elif format == "wx":
        import guiwx
        HEADER = rows[0]
        FOOTER = [rows[-1]]
        TABLE = rows[1:-1]
        guiwx.main(HEADER, TABLE, FOOTER)
    elif format == "django":
        import guidjango
        from guidjango import gui
        HEADER = rows[0]
        FOOTER = [rows[-1]]
        TABLE = rows[1:-1]
        gui.main(HEADER, TABLE, FOOTER)
        

if __name__ == '__main__':    
    _main()