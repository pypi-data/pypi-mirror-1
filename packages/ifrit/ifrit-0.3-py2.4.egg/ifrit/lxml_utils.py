""" ifrit utility implementations using lxml

"""
from lxml.etree import XML as _XML
from lxml.etree import parse as _parse
from lxml.etree import XMLParser

from zope.interface import directlyProvides

from ifrit.interfaces import IStringParser
from ifrit.interfaces import IStreamParser

_parser = XMLParser()

def fromstring(xmlstring):
    return _XML(xmlstring, _parser)

directlyProvides(fromstring, IStringParser)

def parse(xmlstream):
    return _parse(xmlstream, _parser)

directlyProvides(parse, IStreamParser)
