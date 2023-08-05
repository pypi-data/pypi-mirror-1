""" ifrit package interfaces

$Id: interfaces.py,v 1.1 2007/02/07 23:27:48 tseaver Exp $
"""
from zope.interface import Interface

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
