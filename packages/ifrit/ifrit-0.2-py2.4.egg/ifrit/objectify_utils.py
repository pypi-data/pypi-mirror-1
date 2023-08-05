""" ifrit utility implementations using lxml.objectify

"""
from lxml.etree import XMLParser
from lxml.etree import parse as _parse
from lxml.objectify import ObjectifyElementClassLookup
from lxml.objectify import ObjectifiedDataElement
from lxml.objectify import XML as _XML

from zope.interface import directlyProvides
from zope.interface import implements

from ifrit.interfaces import IElement
from ifrit.interfaces import IStringParser
from ifrit.interfaces import IStreamParser

class _MarkableElement(ObjectifiedDataElement):
    implements(IElement)

_lookup = ObjectifyElementClassLookup(tree_class=_MarkableElement)
_parser = XMLParser(remove_blank_text=True)
_parser.setElementClassLookup(_lookup)

def fromstring(xmlstring):
    return _XML(xmlstring, _parser)

directlyProvides(fromstring, IStringParser)

def parse(xmlstream):
    return _parse(xmlstream, _parser)

directlyProvides(parse, IStreamParser)
