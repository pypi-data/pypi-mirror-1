#!/usr/bin/env python

#
# Generated  by generateDS.py.
#

import sys
from string import lower as str_lower
from xml.dom import minidom

import simpletype_memberspecs2_sup as supermod

#
# Globals
#

ExternalEncoding = 'ascii'

#
# Data representation classes
#

class SpecialDateSub(supermod.SpecialDate):
    def __init__(self, SpecialProperty=None, valueOf_=''):
        supermod.SpecialDate.__init__(self, SpecialProperty, valueOf_)
supermod.SpecialDate.subclass = SpecialDateSub
# end class SpecialDateSub


class ExtremeDateSub(supermod.ExtremeDate):
    def __init__(self, ExtremeProperty=None, valueOf_=''):
        supermod.ExtremeDate.__init__(self, ExtremeProperty, valueOf_)
supermod.ExtremeDate.subclass = ExtremeDateSub
# end class ExtremeDateSub



def parse(inFilename):
    doc = minidom.parse(inFilename)
    rootNode = doc.documentElement
    rootObj = supermod.SpecialDate.factory()
    rootObj.build(rootNode)
    # Enable Python to collect the space used by the DOM.
    doc = None
##     sys.stdout.write('<?xml version="1.0" ?>\n')
##     rootObj.export(sys.stdout, 0, name_="SpecialDate",
##         namespacedef_='')
    doc = None
    return rootObj


def parseString(inString):
    doc = minidom.parseString(inString)
    rootNode = doc.documentElement
    rootObj = supermod.SpecialDate.factory()
    rootObj.build(rootNode)
    # Enable Python to collect the space used by the DOM.
    doc = None
##     sys.stdout.write('<?xml version="1.0" ?>\n')
##     rootObj.export(sys.stdout, 0, name_="SpecialDate",
##         namespacedef_='')
    return rootObj


def parseLiteral(inFilename):
    doc = minidom.parse(inFilename)
    rootNode = doc.documentElement
    rootObj = supermod.SpecialDate.factory()
    rootObj.build(rootNode)
    # Enable Python to collect the space used by the DOM.
    doc = None
##     sys.stdout.write('#from simpletype_memberspecs2_sup import *\n\n')
##     sys.stdout.write('import simpletype_memberspecs2_sup as model_\n\n')
##     sys.stdout.write('rootObj = model_.SpecialDate(\n')
##     rootObj.exportLiteral(sys.stdout, 0, name_="SpecialDate")
##     sys.stdout.write(')\n')
    return rootObj


USAGE_TEXT = """
Usage: python ???.py <infilename>
"""

def usage():
    print USAGE_TEXT
    sys.exit(1)


def main():
    args = sys.argv[1:]
    if len(args) != 1:
        usage()
    infilename = args[0]
    root = parse(infilename)


if __name__ == '__main__':
    #import pdb; pdb.set_trace()
    main()


