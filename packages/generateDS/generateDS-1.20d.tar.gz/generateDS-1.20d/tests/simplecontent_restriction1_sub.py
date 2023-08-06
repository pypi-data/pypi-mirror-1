#!/usr/bin/env python

#
# Generated  by generateDS.py.
#

import sys
from string import lower as str_lower
from xml.dom import minidom

import simplecontent_restriction2_sup as supermod

#
# Globals
#

ExternalEncoding = 'ascii'

#
# Data representation classes
#

class IdentifierTypeSub(supermod.IdentifierType):
    def __init__(self, schemeDataURI=None, schemeID=None, schemeAgencyName=None, schemeAgencyID=None, schemeName=None, schemeVersionID=None, schemeURI=None, valueOf_=''):
        supermod.IdentifierType.__init__(self, schemeDataURI, schemeID, schemeAgencyName, schemeAgencyID, schemeName, schemeVersionID, schemeURI, valueOf_)
supermod.IdentifierType.subclass = IdentifierTypeSub
# end class IdentifierTypeSub


class BillOfResourcesIDTypeSub(supermod.BillOfResourcesIDType):
    def __init__(self, schemeDataURI=None, schemeID=None, schemeAgencyName=None, schemeAgencyID=None, schemeName=None, schemeVersionID=None, schemeURI=None, valueOf_=''):
        supermod.BillOfResourcesIDType.__init__(self, schemeDataURI, schemeID, schemeAgencyName, schemeAgencyID, schemeName, schemeVersionID, schemeURI, valueOf_)
supermod.BillOfResourcesIDType.subclass = BillOfResourcesIDTypeSub
# end class BillOfResourcesIDTypeSub


class BillOfMaterialIDTypeSub(supermod.BillOfMaterialIDType):
    def __init__(self, schemeDataURI=None, schemeID=None, schemeAgencyName=None, schemeAgencyID=None, schemeName=None, schemeVersionID=None, schemeURI=None, valueOf_=''):
        supermod.BillOfMaterialIDType.__init__(self, schemeDataURI, schemeID, schemeAgencyName, schemeAgencyID, schemeName, schemeVersionID, schemeURI, valueOf_)
supermod.BillOfMaterialIDType.subclass = BillOfMaterialIDTypeSub
# end class BillOfMaterialIDTypeSub



def parse(inFilename):
    doc = minidom.parse(inFilename)
    rootNode = doc.documentElement
    rootObj = supermod.IdentifierType.factory()
    rootObj.build(rootNode)
    # Enable Python to collect the space used by the DOM.
    doc = None
##     sys.stdout.write('<?xml version="1.0" ?>\n')
##     rootObj.export(sys.stdout, 0, name_="IdentifierType",
##         namespacedef_='')
    doc = None
    return rootObj


def parseString(inString):
    doc = minidom.parseString(inString)
    rootNode = doc.documentElement
    rootObj = supermod.IdentifierType.factory()
    rootObj.build(rootNode)
    # Enable Python to collect the space used by the DOM.
    doc = None
##     sys.stdout.write('<?xml version="1.0" ?>\n')
##     rootObj.export(sys.stdout, 0, name_="IdentifierType",
##         namespacedef_='')
    return rootObj


def parseLiteral(inFilename):
    doc = minidom.parse(inFilename)
    rootNode = doc.documentElement
    rootObj = supermod.IdentifierType.factory()
    rootObj.build(rootNode)
    # Enable Python to collect the space used by the DOM.
    doc = None
##     sys.stdout.write('#from simplecontent_restriction2_sup import *\n\n')
##     sys.stdout.write('import simplecontent_restriction2_sup as model_\n\n')
##     sys.stdout.write('rootObj = model_.IdentifierType(\n')
##     rootObj.exportLiteral(sys.stdout, 0, name_="IdentifierType")
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


