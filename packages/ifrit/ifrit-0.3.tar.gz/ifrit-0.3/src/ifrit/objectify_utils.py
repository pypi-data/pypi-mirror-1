""" ifrit utility implementations using lxml.objectify

Note:  nodes returned from this module can *not* have marker interfaces
       added to them at the instance level, due to restricttions in the
       base class (extension type) required by objectify.

$Id: objectify_utils.py,v 1.4 2007/02/17 18:26:16 tseaver Exp $
"""
from lxml.etree import XMLParser
from lxml.etree import parse as _parse
from lxml.objectify import XML as _XML

from zope.interface import directlyProvides
from zope.interface import implements

from ifrit.interfaces import IStringParser
from ifrit.interfaces import IStreamParser

_parser = XMLParser(remove_blank_text=True)

def fromstring(xmlstring):
    return _XML(xmlstring, _parser)

directlyProvides(fromstring, IStringParser)

def parse(xmlstream):
    return _parse(xmlstream, _parser)

directlyProvides(parse, IStreamParser)
