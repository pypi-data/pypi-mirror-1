# -*- coding: iso-8859-1 -*-
"""Development reports for cutplace."""
import cgi
import coverage
import cProfile
import cStringIO
import keyword
import logging
import optparse
import os
import pstats
import string
import sys
import test_cutplace
import test_all
import token
import tokenize
import unittest

def _testLotsOfCustomers():
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(test_cutplace.LotsOfCustomersTest)
    logging.getLogger("cutplace").setLevel(logging.WARNING)
    logging.getLogger("cutplace").info("hello")
    unittest.TextTestRunner(verbosity=2).run(suite)

def createProfilerReport(targetBasePath):
    assert targetBasePath is not None
    
    # cProfile.run("test_all.main()", targetReportPath)
    itemName = "profile_lotsOfCustomers"
    targetProfilePath = os.path.join(targetBasePath, itemName) + ".profile"
    targetReportPath = os.path.join(targetBasePath, itemName) + ".txt"
    cProfile.run("_testLotsOfCustomers()", targetProfilePath)
    targetReportFile = open(targetReportPath, "w")
    try:
        stats = pstats.Stats(targetProfilePath, stream=targetReportFile)
        stats.sort_stats('cumulative').print_stats("cutplace", 20)
    finally:
        targetReportFile.close()

# Based on code from: <http://code.activestate.com/recipes/491274/>
#
# Code coverage colorization:
#  - S�bastien Martini <sebastien.martini@gmail.com>
#    * 5/24/2006 fixed: bug when code is completely covered (Kenneth Lind).
#
# Original recipe:
#  http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/52298
#
# Original Authors:
#  - J�rgen Hermann
#  - Mike Brown <http://skew.org/~mike/>
#  - Christopher Arndt <http://chrisarndt.de>
#

_VERBOSE = False

_KEYWORD = token.NT_OFFSET + 1
_TEXT    = token.NT_OFFSET + 2

_css_classes = {
    token.NUMBER:       'number',
    token.OP:           'operator',
    token.STRING:       'string',
    tokenize.COMMENT:   'comment',
    token.NAME:         'name',
    token.ERRORTOKEN:   'error',
    _KEYWORD:           'keyword',
    _TEXT:              'text',
}

_HTML_HEADER = """\
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN"
  "http://www.w3.org/TR/html4/loose.dtd">
<html>
<head>
<title>code coverage of %(title)s</title>
<meta http-equiv="Content-Type" content="text/html; charset=iso-8859-1">

<style type="text/css">
pre.code {
    font-style: Lucida,"Courier New";
}
.number {
    color: #0080C0;
}
.operator {
    color: #000000;
}
.string {
    color: #008000;
}
.comment {
    color: #808080;
}
.name {
    color: #000000;
}
.error {
    color: #FF8080;
    border: solid 1.5pt #FF0000;
}
.keyword {
    color: #0000FF;
    font-weight: bold;
}
.text {
    color: #000000;
}
.notcovered {
    background-color: #FFB2B2;
}
</style>

</head>
<body>
"""

_HTML_FOOTER = """\
</body>
</html>
"""

class Parser:
    """ Send colored python source.
    """
    def __init__(self, raw, out=sys.stdout, not_covered=[]):
        """ Store the source text.
        """
        self.raw = string.strip(string.expandtabs(raw))
        self.out = out
        self.not_covered = not_covered  # not covered list of lines
        self.cover_flag = False  # is there a <span> tag opened?

    def format(self):
        """ Parse and send the colored source.
        """
        # store line offsets in self.lines
        self.lines = [0, 0]
        pos = 0
        while 1:
            pos = string.find(self.raw, '\n', pos) + 1
            if not pos: break
            self.lines.append(pos)
        self.lines.append(len(self.raw))

        # parse the source and write it
        self.pos = 0
        text = cStringIO.StringIO(self.raw)
        self.out.write('<pre class="code">\n')
        try:
            tokenize.tokenize(text.readline, self)
        except tokenize.TokenError, ex:
            msg = ex[0]
            line = ex[1][0]
            self.out.write("<h3>ERROR: %s</h3>%s\n" % (
                msg, self.raw[self.lines[line]:]))
        if self.cover_flag:
            self.out.write('</span>')
            self.cover_flag = False
        self.out.write('\n</pre>')

    def __call__(self, toktype, toktext, (srow,scol), (erow,ecol), line):
        """ Token handler.
        """
        if _VERBOSE:
            print "type", toktype, token.tok_name[toktype], "text", toktext,
            print "start", srow,scol, "end", erow,ecol, "<br>"

        # calculate new positions
        oldpos = self.pos
        newpos = self.lines[srow] + scol
        self.pos = newpos + len(toktext)

        if not self.cover_flag and srow in self.not_covered:
            self.out.write('<span class="notcovered">')
            self.cover_flag = True

        # handle newlines
        if toktype in [token.NEWLINE, tokenize.NL]:
            if self.cover_flag:
                self.out.write('</span>')
                self.cover_flag = False

        # send the original whitespace, if needed
        if newpos > oldpos:
            self.out.write(self.raw[oldpos:newpos])

        # skip indenting tokens
        if toktype in [token.INDENT, token.DEDENT]:
            self.pos = newpos
            return

        # map token type to a color group
        if token.LPAR <= toktype and toktype <= token.OP:
            toktype = token.OP
        elif toktype == token.NAME and keyword.iskeyword(toktext):
            toktype = _KEYWORD
        css_class = _css_classes.get(toktype, 'text')

        # send text
        self.out.write('<span class="%s">' % (css_class,))
        self.out.write(cgi.escape(toktext))
        self.out.write('</span>')


class MissingList(list):
    def __init__(self, i):
        list.__init__(self, i)

    def __contains__(self, elem):
        for i in list.__iter__(self):
            v_ = m_ = s_ = None
            try:
                v_ = int(i)
            except ValueError:
                m_, s_ = i.split('-')
            if v_ is not None and v_ == elem:
                return True
            elif (m_ is not None) and (s_ is not None) and \
                     (int(m_) <= elem) and (elem <= int(s_)):
                return True
        return False


def colorize_file(filename, outstream=sys.stdout, not_covered=[]):
    """
    Convert a python source file into colorized HTML.

    Reads file and writes to outstream (default sys.stdout).
    """
    fo = file(filename, 'rb')
    try:
        source = fo.read()
    finally:
        fo.close()
    outstream.write(_HTML_HEADER % {'title': os.path.basename(filename)})
    Parser(source, out=outstream,
           not_covered=MissingList((not_covered and \
                                    not_covered.split(', ')) or \
                                   [])).format()
    outstream.write(_HTML_FOOTER)

def createCoverageReport(targetBasePath):
    # Collect coverage data.
    coverage.erase()
    coverage.start()
    test_all.main()
    coverage.stop()

    # Create report.
    for module in [parsers, test_parsers]:
        f, s, m, mf = coverage.analysis(urllib2)
        # output it in ./urllib2.py.html
        fo = file(os.path.basename(f) + ".html", "wb")
        # colorization
        colorize.colorize_file(f, outstream=fo, not_covered=mf)
        fo.close()

    # print report on stdout
    # coverage.report(urllib2)
    # erase coverage data
    coverage.erase()

if __name__ == '__main__':
    logging.basicConfig()
    logging.getLogger("cutplace").setLevel(logging.WARNING)

    usage = "usage: %prog FOLDER"
    parser = optparse.OptionParser(usage)
    options, others = parser.parse_args()
    if len(others) == 1:
        baseFolder = others[0]
        # createProfilerReport(baseFolder)
        createCoverageReport(baseFolder)
    else:
        sys.stderr.write("%s%s" %("target folder for reports must be specified", os.linesep))
        sys.exit(1)
        