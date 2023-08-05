""" ifrit ZCML directives

$Id: zcml.py,v 1.1 2007/02/08 03:05:18 tseaver Exp $
"""
from zope.component import provideAdapter
from zope.interface import Interface
from zope.schema import TextLine
from zope.configuration.fields import GlobalInterface
from zope.configuration.fields import GlobalObject
from zope.configuration.fields import Path
from zope.configuration.fields import PythonIdentifier
from zope.configuration.fields import Tokens

from ifrit.interfaces import IElement
from ifrit.adapters import ElementMaker

class IPathAdapter(Interface):
    """ Interface for directive which creates a path-based adapter.

    E.g.:

     <ifrit:path_adapter
       for="package.interfaces.IContent"
       name="adapterName"
       path="some_lxml_path"
       marker="package.interfaces.IMyElement"
       module="package.module"
       factory_name="factoryName"
       />

    o Create an adapter factory which uses 'path' to extract a node
      from the serialized XML, and stamps the node with the marker
      interface passed in 'marker'.

    o Bind that factory into 'module' under 'factory_name'.

    o Register that factory as providing an 'IElement' adapter for
      the 'for' interface, using the 'name' if provided (otherwise,
      registers it as the default adapter).
    """
    module = GlobalObject(
        title=u"Target module",
        description=u"Module into which the generated adapter factory "
                    u"will be added.",
        required=True,
        )

    factory_name = PythonIdentifier(
        title=u"Factory name",
        description=u"Name of the generated adapter factory.",
        required=True,
        )

    path = TextLine(
        title=u"Path",
        description=u"XPath or ElementTree path expression",
        required=True,
        )

    for_ = Tokens(
        title=u"Specifications to be adapted",
        description=u"This should be a list of interfaces or classes",
        value_type=GlobalObject(missing_value=object()),
        required=False,
        )

    name = PythonIdentifier(
        title=u"Adapter name",
        description=u"Name under which the adapter is registered.",
        required=False,
        )

    marker = GlobalInterface(
        title=u"Merker Interface",
        description=u"Interface to be stamped onto adapters",
        required=False,
        )


def createPathAdapter(module, factory_name, path,
                      for_=None, name='', marker=None):
    """ Create an adapter factory using 'path'.
 
    o Seat the new schema into 'module' under 'factory_name'.
    """
    if marker is None:
        marker = IElement
    factory = ElementMaker(path, marker)
    setattr(module, factory_name, factory)
    provideAdapter(factory, for_, IElement, name)

def PathAdapterDirective(_context, module, factory_name, path,
                         for_=None, name='', marker=None):
    # Directive handler for <ifrit:path_adapter> directive.
    _context.action(
        discriminator = (module, factory_name,),
        callable = createPathAdapter,
        args = (module, factory_name, path, for_, name, marker),
        )
