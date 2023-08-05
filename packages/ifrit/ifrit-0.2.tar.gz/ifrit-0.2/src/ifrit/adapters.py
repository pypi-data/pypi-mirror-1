""" ifrist adapters

$Id: adapters.py,v 1.3 2007/02/09 21:41:42 tseaver Exp $
"""
import warnings

from StringIO import StringIO

from zope.component import getUtility
from zope.interface import implements
from zope.interface import classImplements
from zope.interface import directlyProvides

from ifrit.interfaces import IElement
from ifrit.interfaces import IElementFactory
from ifrit.interfaces import IStreamParser
from ifrit.interfaces import IStringParser
from ifrit.interfaces import IXMLSerialization

class OFSFileAsXML(object):
    """ "Convert" OFS.Image.File-like object to XML.

    o Assume that the 'data' element is a string, unicode, or a pdata chunk,
      containing the actual XML to be returned.
    """
    implements(IXMLSerialization)

    def __init__(self, context):
        self.context = context

    def serialize(self, buffer):
        data = self.context.data
        if isinstance(data, str):
            buffer.write(data)
        elif isinstance(data, unicode):
            buffer.write(data.encode('utf8'))
        else:
            while data is not None:
                buffer.write(data.data)
                data = data.next

class ElementMaker(object):
    """ Adapter factories which use paths to find nodes.
    """
    implements(IElementFactory)

    def __init__(self, path=None, marker=IElement, parser_name=None):
        self.path = path
        self.marker = marker
        self.parser_name = parser_name or 'elementtree'

    def __call__(self, context):
        buffer = StringIO()

        adapter = IXMLSerialization(context)
        adapter.serialize(buffer)
        buffer.seek(0)

        parser = getUtility(IStreamParser, name=self.parser_name)
        tree = parser(buffer).getroot()

        if self.path is not None:
            node = tree.find(self.path)
        else:
            node = tree

        if node is not None:
            directlyProvides(node, self.marker)

        return node
