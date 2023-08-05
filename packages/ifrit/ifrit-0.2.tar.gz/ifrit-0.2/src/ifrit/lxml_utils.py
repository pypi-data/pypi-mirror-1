""" ifrit utility implementations using lxml

"""
from lxml.etree import XML as _XML
from lxml.etree import parse as _parse
from lxml.etree import ElementBase
from lxml.etree import ElementDefaultClassLookup
from lxml.etree import XMLParser

from zope.interface import directlyProvides
from zope.interface import implements

from ifrit.interfaces import IElement
from ifrit.interfaces import IStringParser
from ifrit.interfaces import IStreamParser

class _MarkableElement(ElementBase):
    implements(IElement)

_lookup = ElementDefaultClassLookup(element=_MarkableElement)
_parser = XMLParser()
_parser.setElementClassLookup(_lookup)

def fromstring(xmlstring):
    return _XML(xmlstring, _parser)

directlyProvides(fromstring, IStringParser)

def parse(xmlstream):
    return _parse(xmlstream, _parser)

directlyProvides(parse, IStreamParser)
