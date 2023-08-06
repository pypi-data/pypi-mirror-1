#!/usr/bin/env python

#
# Generated  by generateDS.py.
#

import sys
from string import lower as str_lower
from xml.dom import minidom

import anysimpletype2_sup as supermod

#
# Globals
#

ExternalEncoding = 'ascii'

#
# Data representation classes
#

class test1elementSub(supermod.test1element):
    def __init__(self, test1attribute=None, test1member=None):
        supermod.test1element.__init__(self, test1attribute, test1member)
supermod.test1element.subclass = test1elementSub
# end class test1elementSub


class cimAnySimpleTypeSub(supermod.cimAnySimpleType):
    def __init__(self, valueOf_=''):
        supermod.cimAnySimpleType.__init__(self, valueOf_)
supermod.cimAnySimpleType.subclass = cimAnySimpleTypeSub
# end class cimAnySimpleTypeSub



def parse(inFilename):
    doc = minidom.parse(inFilename)
    rootNode = doc.documentElement
    rootObj = supermod.test1element.factory()
    rootObj.build(rootNode)
    # Enable Python to collect the space used by the DOM.
    doc = None
##     sys.stdout.write('<?xml version="1.0" ?>\n')
##     rootObj.export(sys.stdout, 0, name_="test1element",
##         namespacedef_='')
    doc = None
    return rootObj


def parseString(inString):
    doc = minidom.parseString(inString)
    rootNode = doc.documentElement
    rootObj = supermod.test1element.factory()
    rootObj.build(rootNode)
    # Enable Python to collect the space used by the DOM.
    doc = None
##     sys.stdout.write('<?xml version="1.0" ?>\n')
##     rootObj.export(sys.stdout, 0, name_="test1element",
##         namespacedef_='')
    return rootObj


def parseLiteral(inFilename):
    doc = minidom.parse(inFilename)
    rootNode = doc.documentElement
    rootObj = supermod.test1element.factory()
    rootObj.build(rootNode)
    # Enable Python to collect the space used by the DOM.
    doc = None
##     sys.stdout.write('#from anysimpletype2_sup import *\n\n')
##     sys.stdout.write('import anysimpletype2_sup as model_\n\n')
##     sys.stdout.write('rootObj = model_.test1element(\n')
##     rootObj.exportLiteral(sys.stdout, 0, name_="test1element")
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


