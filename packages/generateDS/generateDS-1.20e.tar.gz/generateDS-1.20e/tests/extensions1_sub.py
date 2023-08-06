#!/usr/bin/env python

#
# Generated  by generateDS.py.
#

import sys
from string import lower as str_lower
from xml.dom import minidom

import extensions2_sup as supermod

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


class singleExtremeDateSub(supermod.singleExtremeDate):
    def __init__(self, ExtremeProperty=None, valueOf_=''):
        supermod.singleExtremeDate.__init__(self, ExtremeProperty, valueOf_)
supermod.singleExtremeDate.subclass = singleExtremeDateSub
# end class singleExtremeDateSub


class containerTypeSub(supermod.containerType):
    def __init__(self, simplefactoid=None, mixedfactoid=None):
        supermod.containerType.__init__(self, simplefactoid, mixedfactoid)
supermod.containerType.subclass = containerTypeSub
# end class containerTypeSub


class simpleFactoidTypeSub(supermod.simpleFactoidType):
    def __init__(self, relation=None):
        supermod.simpleFactoidType.__init__(self, relation)
supermod.simpleFactoidType.subclass = simpleFactoidTypeSub
# end class simpleFactoidTypeSub


class mixedFactoidTypeSub(supermod.mixedFactoidType):
    def __init__(self, relation=None, valueOf_='', mixedclass_=None, content_=None):
        supermod.mixedFactoidType.__init__(self, valueOf_, mixedclass_, content_)
supermod.mixedFactoidType.subclass = mixedFactoidTypeSub
# end class mixedFactoidTypeSub


class BaseTypeSub(supermod.BaseType):
    def __init__(self, BaseProperty1=None, BaseProperty2=None, valueOf_=''):
        supermod.BaseType.__init__(self, BaseProperty1, BaseProperty2, valueOf_)
supermod.BaseType.subclass = BaseTypeSub
# end class BaseTypeSub


class DerivedTypeSub(supermod.DerivedType):
    def __init__(self, BaseProperty1=None, BaseProperty2=None, DerivedProperty1=None, DerivedProperty2=None, valueOf_=''):
        supermod.DerivedType.__init__(self, BaseProperty1, BaseProperty2, DerivedProperty1, DerivedProperty2, valueOf_)
supermod.DerivedType.subclass = DerivedTypeSub
# end class DerivedTypeSub


class MyIntegerSub(supermod.MyInteger):
    def __init__(self, MyAttr=None, valueOf_=''):
        supermod.MyInteger.__init__(self, MyAttr, valueOf_)
supermod.MyInteger.subclass = MyIntegerSub
# end class MyIntegerSub


class MyBooleanSub(supermod.MyBoolean):
    def __init__(self, MyAttr=None, valueOf_=''):
        supermod.MyBoolean.__init__(self, MyAttr, valueOf_)
supermod.MyBoolean.subclass = MyBooleanSub
# end class MyBooleanSub


class MyFloatSub(supermod.MyFloat):
    def __init__(self, MyAttr=None, valueOf_=''):
        supermod.MyFloat.__init__(self, MyAttr, valueOf_)
supermod.MyFloat.subclass = MyFloatSub
# end class MyFloatSub


class MyDoubleSub(supermod.MyDouble):
    def __init__(self, MyAttr=None, valueOf_=''):
        supermod.MyDouble.__init__(self, MyAttr, valueOf_)
supermod.MyDouble.subclass = MyDoubleSub
# end class MyDoubleSub



def parse(inFilename):
    doc = minidom.parse(inFilename)
    rootNode = doc.documentElement
    rootObj = supermod.containerType.factory()
    rootObj.build(rootNode)
    # Enable Python to collect the space used by the DOM.
    doc = None
##     sys.stdout.write('<?xml version="1.0" ?>\n')
##     rootObj.export(sys.stdout, 0, name_="container",
##         namespacedef_='')
    doc = None
    return rootObj


def parseString(inString):
    doc = minidom.parseString(inString)
    rootNode = doc.documentElement
    rootObj = supermod.containerType.factory()
    rootObj.build(rootNode)
    # Enable Python to collect the space used by the DOM.
    doc = None
##     sys.stdout.write('<?xml version="1.0" ?>\n')
##     rootObj.export(sys.stdout, 0, name_="container",
##         namespacedef_='')
    return rootObj


def parseLiteral(inFilename):
    doc = minidom.parse(inFilename)
    rootNode = doc.documentElement
    rootObj = supermod.containerType.factory()
    rootObj.build(rootNode)
    # Enable Python to collect the space used by the DOM.
    doc = None
##     sys.stdout.write('#from extensions2_sup import *\n\n')
##     sys.stdout.write('import extensions2_sup as model_\n\n')
##     sys.stdout.write('rootObj = model_.container(\n')
##     rootObj.exportLiteral(sys.stdout, 0, name_="container")
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


