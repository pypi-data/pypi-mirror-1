""" ifrit ZCML directives

$Id: zcml.py,v 1.6 2007/02/17 19:48:15 tseaver Exp $
"""
from zope.component import provideAdapter
from zope.interface import Interface
from zope.schema import TextLine
from zope.configuration.fields import GlobalInterface
from zope.configuration.fields import GlobalObject
from zope.configuration.fields import Path
from zope.configuration.fields import PythonIdentifier
from zope.configuration.fields import Tokens
from zope.configuration.fields import Bool
from zope.publisher.interfaces import IPublishTraverse
from zope.publisher.interfaces import IRequest

from ifrit.interfaces import IElement
from ifrit.adapters import ElementMaker
from ifrit.adapters import ElementTraversalAdapterFactory

class IPathAdapter(Interface):
    """ Interface for directive which creates a path-based adapter.

    E.g.:

     <ifrit:path_adapter
       for="package.interfaces.IContent"
       name="adapterName"
       path="some_lxml_path"
       parser_name="objectify"
       module="package.module"
       factory_name="factoryName"
       />

    o Create an adapter factory which uses 'path' to extract a node
      from the serialized XML, as parsed by the utility identifed
      by 'parser_name'.

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

    parser_name = PythonIdentifier(
        title=u"Parser name",
        description=u"Name of IStreamParser utility used to parse XML",
        required=False,
        default=u'elementtree'
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

    multiple = Bool(
        title=u"Multiple",
        description=u"Does the factory return a sequence?",
        required=False,
        default=False,
        )


def createPathAdapter(module, factory_name, path, parser_name,
                      for_, name, multiple):
    """ Create an adapter factory using 'path'.
 
    o Seat the new schema into 'module' under 'factory_name'.
    """
    factory = ElementMaker(path, parser_name, multiple)
    setattr(module, factory_name, factory)
    provideAdapter(factory, for_, IElement, name)

def PathAdapterDirective(_context,
                         module,
                         factory_name,
                         path,
                         parser_name='elementtree',
                         for_=None,
                         name='',
                         multiple=False,
                        ):
    # Directive handler for <ifrit:path_adapter> directive.
    _context.action(
        discriminator = (module, factory_name,),
        callable = createPathAdapter,
        args = (module,
                factory_name,
                path,
                parser_name,
                for_,
                name,
                multiple,
               ),
        )

class ITraversalAdapter(Interface):
    """ Interface for directive which creates a traveral adapter factory.

    E.g.:

     <ifrit:traversal_adapter
        for="ifrit.tests.IDummy"
        module="ifrit.tests"
        factory_name="traversalFactory">
      <ifrit:marker
        name="items"
        interface="ifrit.tests.IMarker"
     </ifrit:traversal_adapter>

    o Create a traversal adapter factory, which stamps the returned node
      with the marker interface passed in the corresponding 'marker'.

    o Bind that factory into 'module' under 'factory_name'.

    o Register that factory as providing the default 'IPathTraverser' adapter
      for the 'for' interface.
    """
    module = GlobalObject(
        title=u"Target module",
        description=u"Module into which the generated adapter factory "
                    u"will be added.",
        required=True,
        )

    factory_name = PythonIdentifier(
        title=u"Factory name",
        description=u"Name of the generated traversal adapter factory.",
        required=True,
        )

    for_ = Tokens(
        title=u"Specifications to be adapted",
        description=u"This should be a list of interfaces or classes",
        value_type=GlobalObject(missing_value=object()),
        required=False,
        )

class ITraversalMarkerDirective(Interface):
    """ Sub-directive schema for <ifrit:marker>.
    """
    name = PythonIdentifier(
        title=u"Traversal name",
        description=u"Name traversed by the adapter.",
        required=True,
        )

    interface = GlobalInterface(
        title=u"Merker Interface",
        description=u"Interface to be stamped onto returned nodes",
        required=False,
        )

def createTraversalAdapter(module, factory_name, for_, markers):
    """ Create an adapter factory using 'path'.
 
    o Seat the new schema into 'module' under 'factory_name'.
    """
    factory = ElementTraversalAdapterFactory(markers)
    setattr(module, factory_name, factory)
    provideAdapter(factory, for_, IPublishTraverse)
    provideAdapter(factory, for_ + (IRequest,), IPublishTraverse)

class TraversalAdapterDirective(object):

    def __init__(self, _context, module, factory_name, for_=None):
        # Directive handler for <ifrit:traversal_adapter> directive.
        self._context = _context
        self.module = module
        self.factory_name = factory_name
        self.for_ = for_
        self._markers = {}

    def marker(self, context, name, interface):
        self._markers[name] = interface

    def __call__(self):

        for_ = tuple(self.for_)
        self._context.action(
            discriminator=('adapter', for_, IPublishTraverse, ''),
            callable=createTraversalAdapter,
            args=(self.module, self.factory_name, for_, self._markers),
            )


