""" ifrit package interfaces

$Id: interfaces.py,v 1.2 2007/02/09 21:41:42 tseaver Exp $
"""
from zope.interface import Interface

class IStringParser(Interface):
    """ Utility interface for a parser which can be called passing a string.

    o Examples:  elementtree.ElementTree.XML
    """
    def __call__(xmlstring):
        """ Parse 'xmlstring', and return the root ElementTree node.
        """

class IStreamParser(Interface):
    """ Utility interface for a parser which can be called passing a stream.

    o Examples:  elementtree.ElementTree.parse
    """
    def __call__(xmlstream):
        """ Parse 'xmlstream', and return the root ElementTree node.
        """

class IElement(Interface):
    """ Adapter interface.
    """

class IElementFactory(Interface):
    """ Adapter factory interface.
    """
    def __call__(context):
        """ Adapt context to an element interface
        
        o Adapted object will provide an interface derived from IElement.
        """

class IXMLSerialization(Interface):
    """ Utility interface.
    """
    def serialize(buffer):
        """ Write an XML representation of 'context' into 'buffer'.
        """
