#!/usr/bin/env python

#
# Generated  by generateDS.py.
#

import sys
from string import lower as str_lower
from xml.dom import minidom

import out2sup as supermod

#
# Globals
#

ExternalEncoding = 'ascii'

#
# Data representation classes
#

class peopleSub(supermod.people):
    def __init__(self, person=None):
        supermod.people.__init__(self, person)
supermod.people.subclass = peopleSub
# end class peopleSub


class personSub(supermod.person):
    def __init__(self, id=None, value=None, ratio_attr=None, name=None, ratio=None, imagesize=None, interest=None, category=None, hot_agent=None, promoter=None, hot=None):
        supermod.person.__init__(self, id, value, ratio_attr, name, ratio, imagesize, interest, category, hot_agent, promoter, hot)
supermod.person.subclass = personSub
# end class personSub


class BasicEmptyTypeSub(supermod.BasicEmptyType):
    def __init__(self, valueOf_=''):
        supermod.BasicEmptyType.__init__(self, valueOf_)
supermod.BasicEmptyType.subclass = BasicEmptyTypeSub
# end class BasicEmptyTypeSub


class hot_agentSub(supermod.hot_agent):
    def __init__(self, firstname=None, lastname=None, priority=None):
        supermod.hot_agent.__init__(self, firstname, lastname, priority)
supermod.hot_agent.subclass = hot_agentSub
# end class hot_agentSub


class boosterSub(supermod.booster):
    def __init__(self, firstname=None, lastname=None, client=None):
        supermod.booster.__init__(self, firstname, lastname, client)
supermod.booster.subclass = boosterSub
# end class boosterSub


class clientSub(supermod.client):
    def __init__(self, fullname=None, refid=None):
        supermod.client.__init__(self, fullname, refid)
supermod.client.subclass = clientSub
# end class clientSub



def parse(inFilename):
    doc = minidom.parse(inFilename)
    rootNode = doc.documentElement
    rootObj = supermod.people.factory()
    rootObj.build(rootNode)
    # Enable Python to collect the space used by the DOM.
    doc = None
    sys.stdout.write('<?xml version="1.0" ?>\n')
    rootObj.export(sys.stdout, 0, name_="people",
        namespacedef_='')
    doc = None
    return rootObj


def parseString(inString):
    doc = minidom.parseString(inString)
    rootNode = doc.documentElement
    rootObj = supermod.people.factory()
    rootObj.build(rootNode)
    # Enable Python to collect the space used by the DOM.
    doc = None
    sys.stdout.write('<?xml version="1.0" ?>\n')
    rootObj.export(sys.stdout, 0, name_="people",
        namespacedef_='')
    return rootObj


def parseLiteral(inFilename):
    doc = minidom.parse(inFilename)
    rootNode = doc.documentElement
    rootObj = supermod.people.factory()
    rootObj.build(rootNode)
    # Enable Python to collect the space used by the DOM.
    doc = None
    sys.stdout.write('from out2sup import *\n\n')
    sys.stdout.write('rootObj = people(\n')
    rootObj.exportLiteral(sys.stdout, 0, name_="people")
    sys.stdout.write(')\n')
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


