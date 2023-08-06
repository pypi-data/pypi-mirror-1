#!/usr/bin/env python
# _*_ coding: UTF-8 _*_

"""A fileinfo plug-in for Python source files.
"""


import tokenize, cStringIO, keyword, re, operator
from tokenize import NAME, NEWLINE, NL, COMMENT, STRING, OP, INDENT

from fileinfo.compatibility import *
from fileinfo.investigator import BaseInvestigator


def countStaticImportStatements(toks):
    "Count static import statements in sequence of Python tokens."
    
    stmts = []
    stmt = []
    currKw = None
    for tokEntry in toks:
        code, tok, start, end, line = tokEntry
        if code == NAME and tok in ("from", "import"):
            if currKw == None:
                stmt = []
            currKw = tok
            stmt.append(tok)
        elif code == NEWLINE and tok == "\n":
            if currKw != None:
                stmts.append(stmt)
                stmt = []
            currKw = None
        elif currKw != None:
            stmt.append(tok)
    if stmt:
        stmts.append(stmt)

    # from pprint import pprint as pp
    # pp(stmts)
    return stmts


def countImportedSources(toks):
    "Count imported symbols from Python tokens."
    
    stmts = countStaticImportStatements(toks)

    for s in stmts:
        if s[0] == "import":
            while True:
                try:
                    pos = s.index("as")
                except ValueError:
                    break
                del s[pos:pos+2]
            
    imports = [s[1:] for s in stmts if s[0] == "import"]
    froms = [s[1:s.index("import")] for s in stmts if s[0] == "from"]
    
    imports = ["".join(i) for i in imports]
    imports = [i.split(",") for i in imports]
    imports = reduce(operator.add, imports, [])
    # print "imports", imports

    froms = ["".join(i) for i in froms]
    # print "froms", froms
    
    all = imports + froms
    # print "all", set(all)
    
    return set(all)
    
    
def countDocstrings(toks, verbose=False):
    "Count docstrings in Python code tokens."
    
    docstrings = []

    # first, find module doc string, if present
    i = 0
    while i < len(toks):
        code, tok, start, end, line = toks[i]
        i += 1
        if code in (COMMENT, NL):
            continue
        elif code == STRING:
            docstrings.append(tok)
            while i < len(toks):
                code, tok, start, end, line = toks[i]
                i += 1
                if code == STRING:
                    docstrings[-1] += tok
                else:
                    break
            break
        else:
            break

    # now, find class docstrings, if present

    # search class keyword
    j = i
    for kw in ("class", "def"):
        i = j
        while i < len(toks):
            code, tok, start, end, line = toks[i]
            if code == NAME and tok == kw:
                # found class/def keyword
                if verbose: 
                    print toks[i]
                column = start[1]
                i += 1
                while i < len(toks):
                    code, tok, start, end, line = toks[i]
                    # search ":" at end of class/def header
                    if code == OP and tok == ":":
                        if verbose: 
                            print toks[i]
                        i += 1
                        # skip newline, indent and comment...
                        while i < len(toks):
                            code, tok, start, end, line = toks[i]
                            i += 1
                            if code in (NEWLINE, INDENT, COMMENT):
                                continue
                            # ... take first string
                            elif code == STRING:
                                if verbose: 
                                    print toks[i]
                                docstrings.append(tok)
                                while i < len(toks):
                                    code, tok, start, end, line = toks[i]
                                    i += 1
                                    if code == STRING:
                                        docstrings[-1] += tok
                                    else:
                                        break
                                break
                            else:
                                break
                        break
                    i += 1
            i += 1
                
    return docstrings


class PyInvestigator(BaseInvestigator):
    "A class for determining attributes of TrueType files."

    attrMap = {
        "bang": "getBangLine",
        "nclasses": "getNumClasses",
        "ndefs": "getNumDefs",
        "nops": "getNumOps",
        "ndecs": "getNumDecorators",
        "decs": "getDecorators",
        "ncomments": "getNumComments",
        "nstrs": "getNumStrings",
        "ndocstrs": "getNumDocstrings",
        "nkws": "getNumKeywords",
        "ndkws": "getNumDiffkeywords",
        "nimpstmts": "getNumImportStatements",
        "nimpsrcs": "getNumImportedSources",
        "impsrcs": "getImportedSources",
        "ncalls": "getNumCalls",
        "nmtlines": "getNumEmptyLines",
        "mlw": "getMaxLineWidth",
        "mil": "getMaxIndentLevel",
        "enc": "getEncoding",
    }

    totals = (
        "nclasses", "ndefs", "nops", "ncomments", "nstrs", "ndocstrs", 
        "nkws", "ndkws", "nimpstmts", "nimpsrcs", "ncalls", "nmtlines", 
        "ndecs",
    )

    def activate(self):
        "Try activating self, setting 'active' variable."

        # print "***", self.path
        self.content = open(self.path, "rU").read()
        self.tokens = []
        gt = tokenize.generate_tokens
        try:
            self.tokens = list(gt(cStringIO.StringIO(self.content).readline))
            self.active = True
        except: # (IOError, tokenize.TokenError):
            self.active = False
            
        return self.active


    def getBangLine(self):
        "Return Boolean if Python file contains a slash bang line."

        t0 = self.tokens[0]
        if t0[0] == COMMENT and t0[1].startswith("#!"):
            return True
        else:
            return False


    def getNumComments(self):
        "Return number of Python comments."

        # from fileinfo.test import tokenit
        toks = [t for t in self.tokens if t[0] == COMMENT]
        # toks = [map(repr, t) for t in toks if t[0] > 0]
        # tokenit.displayAsTable(toks)
        return len(toks)


    def getNumClasses(self):
        "Return number of Python classes."

        toks = [t for t in self.tokens if t[:2] == (NAME, "class")]
        return len(toks)


    def getNumDefs(self):
        "Return number of Python functions or methods."

        toks = [t for t in self.tokens if t[:2] == (NAME, "def")]
        return len(toks)


    def getNumOps(self):
        "Return number of Python operators."

        # anything from ".,:;()[]{}+-*/="
        toks = [t for t in self.tokens if t[0] == OP]
        return len(toks)


    def getNumDecorators(self):
        "Return number of Python decorators."

        toks = [t for t in self.tokens if t[:2] == (OP, "@")]
        return len(toks)


    def getDecorators(self):
        "Return sorted unique list of all Python decorators."

        enumDecoToks = [(i, t) for (i, t) in enumerate(self.tokens) 
            if t[:2] == (OP, "@")]

        decorators = []
        for i, t in enumDecoToks:
            deco = ""
            while True:
                i += 1
                t = self.tokens[i]
                if t[0] == NAME or t[:2] == (OP, "."):
                    deco += t[1]
                else:
                    break
            decorators.append(deco)
        
        return sorted(set(decorators))


    def getNumStrings(self):
        "Return number of Python strings."

        toks = [t for t in self.tokens if t[0] == STRING]
        return len(toks)


    def getNumDocstrings(self):
        "Return number of Python docstrings."

        return len(countDocstrings(self.tokens))


    def getNumKeywords(self):
        "Return number of Python keywords."

        kwlist = keyword.kwlist
        toks = [t for t in self.tokens if t[0] == NAME and t[1] in kwlist]
        return len(toks)


    def getNumDiffkeywords(self):
        "Return number of different Python keywords."

        kwlist = keyword.kwlist
        kws = [t[1] for t in self.tokens if t[0] == NAME and t[1] in kwlist]
        return len(set(kws))
        
        
    def getNumImportStatements(self):
        "Return number of static Python import statements."

        return len(countStaticImportStatements(self.tokens))
        
        
    def getNumImportedSources(self):
        "Return number of statically imported Python sources."

        # e.g. 
        # import x; from y import z
        # -> 2
        
        return len(countImportedSources(self.tokens))
        

    def getImportedSources(self):
        "Return sorted unique list of statically imported Python sources."

        # e.g. 
        # import x; from y import z
        # -> ['x', 'y']

        res = list(countImportedSources(self.tokens))
        res.sort()
        return res
        

    def getNumEmptyLines(self):
        "Return number of empty lines in Python code."
        
        return len([tok for tok in self.tokens if tok[0] == NL])


    def getMaxLineWidth(self):
        "Return max. line width."
        
        return max([len(line) for line in self.content.split("\n")])


    def getMaxIndentLevel(self):
        "Return max. indent level."
        
        indents = [len(tok[1]) for tok in self.tokens if tok[0] == INDENT]
        indents = list(set(indents))
        return len(indents)

        
    def getEncoding(self):
        "Return file encoding."
        
        pat = re.compile("# _\*_ coding: *([\-\w]+) *_\*_\n")
        for tok in self.tokens:
            if tok[0] != COMMENT:
                break
            else:
                m = pat.match(tok[1])
                if m:
                    return m.groups()[0]
        return None


    def getNumCalls(self):
        "Return number of static calls."
        
        # filter tokens
        toksf = [t for (i, t) in enumerate(self.tokens) 
            if (t[0]==NAME  and self.tokens[i-1][1] not in ("class", "def")) or 
                t[0] in (OP, NL, NEWLINE) 
        ]
        toksff = []
        tlast = None
        for t in toksf:
            if t[0] == NAME:
                if tlast and tlast[0] == NAME:
                    tlast = t
                    toksff[-1] = t
                else:
                    toksff.append(t)
                    tlast = t
            else:
                toksff.append(t)
                tlast = t
    
        # join tokens
        tokString = "".join([t[1] for t in toksff])
    
        # search all call patterns    
        pat = re.compile("([\w\.]+)\(")
        calls = re.findall(pat, tokString)
        
        # remove keywords
        calls = [c for c in calls if c not in keyword.kwlist]
        
        # return list(set(calls))
        return len(calls)
