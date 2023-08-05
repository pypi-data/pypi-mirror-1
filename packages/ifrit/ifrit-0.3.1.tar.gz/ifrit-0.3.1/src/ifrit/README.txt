ifrit -- Elemental XML Adapters
===============================

Overview
--------

This package provides support for writing Zope3 component architecture
adapters which extract ElementTree nodes from content, stamping them
with marker interface declarations.  Such nodes can then be further adapted,
including lookup of views, etc.

The package defines two adapter interfaces of interest::

  >>> from ifrit.interfaces import IXMLSerialization
  >>> from ifrit.interfaces import IElement

``IXMLSerialization`` adapters take a buffer object, and write an XML
representation of their cont nt into that buffer.  ``IElement`` objects
are instances of classes defined to subclass ``ElementTree._Element``,
or its ``lxml`` equivalent.


Serializing Content to XML
--------------------------

First, define a content object we can adapt::

  >>> from zope.component.testing import setUp, tearDown
  >>> setUp()
  >>> from zope.interface import Interface, implements
  >>> class IDummy(Interface):
  ...     pass
  >>> class Dummy:
  ...     implements(IDummy)
  ...     def __init__(self, name, items=()):
  ...         self.name = name
  ...         self.items = items
  >>> dummy = Dummy('testing')

Now, define and register the serializer adapter::

  >>> class DummyAsXML:
  ...     implements(IXMLSerialization)
  ...     def __init__(self, context):
  ...         self.context = context
  ...     def serialize(self, buffer):
  ...         items = ['<item>%s</item>' % x for x in self.context.items]
  ...         template = '<dummy>%s<items>%s</items></dummy>'
  ...         buffer.write(template % (self.context.name, ''.join(items)))
  >>> from zope.app.testing import ztapi
  >>> ztapi.provideAdapter(IDummy, IXMLSerialization, DummyAsXML)

Now we can try the adapter out::

  >>> serializer = IXMLSerialization(dummy)
  >>> from StringIO import StringIO
  >>> buffer = StringIO()
  >>> serializer.serialize(buffer)
  >>> buffer.getvalue()
  '<dummy>testing<items></items></dummy>'

If the Dummy object has items, they get rendered::

  >>> with_items = Dummy('with_items', ('a', 'b'))
  >>> buffer = StringIO()
  >>> serializer = IXMLSerialization(with_items)
  >>> serializer.serialize(buffer)
  >>> buffer.getvalue()
  '<dummy>with_items<items><item>a</item><item>b</item></items></dummy>'


Adapting Content to ETree Nodes
-------------------------------

The package provides an adapter generator for ``IElement`` adapters, based
on path expressions (the process depends on having an ``IXMLSerialization``
adapter already registered for the context)

First, register a parser utility ('elementtree' is the default used by
ElementMaker)::

  >>> from elementtree.ElementTree import parse
  >>> from zope.component import provideUtility
  >>> from ifrit.interfaces import IStreamParser
  >>> provideUtility(parse, IStreamParser, 'elementtree')

Now we can create our adapter generator::

  >>> from ifrit.adapters import ElementMaker
  >>> d_factory = ElementMaker()
  >>> ztapi.provideAdapter(IDummy, IElement, d_factory)
  >>> i_factory = ElementMaker(path='items')
  >>> ztapi.provideAdapter(IDummy, IElement, i_factory, name='items')
  >>> d_node = IElement(dummy)
  >>> d_node.tag
  'dummy'
  >>> d_node.text
  'testing'

Sigh, we can't pass ``name`` to an interface-call shortcut::

  >>> from zope.component import getAdapter
  >>> i_node = getAdapter(dummy, IElement, name='items')
  >>> i_node.tag
  'items'

  >>> i_node = getAdapter(with_items, IElement, name='items')
  >>> sub = i_node.findall('item')
  >>> [x.text for x in sub]
  ['a', 'b']


Traversing Content for Publishing
---------------------------------

We'd like to be able to traverse a content object via a URL, and get
back a child node.  In order for such a child node to be useful, it
will need to have some extra attributes:  ``__parent__`` and ``__name__``,
so that the object plays well with Zope's "location" machinery, and
``__provides__``, so that we can do view and adapter lookup on the child::

  >>> class IMarker(Interface): pass
  >>> _MARKERS = {'items': IMarker}
  >>> from zope.publisher.interfaces.browser import IBrowserRequest
  >>> class DummyRequest(object): implements(IBrowserRequest)
  >>> request = DummyRequest()
  >>> from ifrit.adapters import ElementTraversalAdapter
  >>> traverser = ElementTraversalAdapter(dummy, markers=_MARKERS)
  >>> target = traverser.publishTraverse(request, 'items')
  >>> target.__parent__ is dummy
  True
  >>> target.__name__
  'items'
  >>> IMarker.providedBy(target)
  True


Creating Path Adapters in ZCML
------------------------------

The package provides a custom ZCML directive which creates an adapter
factory::

  >>> import ifrit.tests
  >>> ifrit.tests.IDummy = IDummy
  >>> from zope.configuration.xmlconfig import file as zcml_file
  >>> from zope.configuration.xmlconfig import string as zcml_string
  >>> context = zcml_file('meta.zcml', package=ifrit)
  >>> _PATH_ZCML = """\
  ... <configure xmlns="http://namespaces.zope.org/zope"
  ...            xmlns:ifrit="http://namespaces.zope.org/ifrit">
  ...   <ifrit:path_adapter
  ...      for="ifrit.tests.IDummy"
  ...      name="alternate"
  ...      path="items"
  ...      parser_name="elementtree"
  ...      module="ifrit.tests"
  ...      factory_name="alternateFactory" />
  ... </configure>"""   
  >>> ignored = zcml_string(_PATH_ZCML, context=context)
  >>> isinstance(ifrit.tests.alternateFactory, ElementMaker)
  True
  >>> ifrit.tests.alternateFactory.path == 'items'
  True
  >>> adapter = getAdapter(dummy, IElement, name='alternate')
  >>> adapter.tag
  'items'


Creating Traversal Adapters in ZCML
-----------------------------------

We can also register traversal adapters via ZCML::

  >>> from ifrit.adapters import ElementTraversalAdapterFactory
  >>> ifrit.tests.IMarker = IMarker
  >>> _TRAVERSAL_ZCML = """\
  ... <configure xmlns="http://namespaces.zope.org/zope"
  ...            xmlns:ifrit="http://namespaces.zope.org/ifrit">
  ...   <ifrit:traversal_adapter
  ...      for="ifrit.tests.IDummy"
  ...      module="ifrit.tests"
  ...      factory_name="traversalFactory">
  ...    <ifrit:marker
  ...      name="items"
  ...      interface="ifrit.tests.IMarker"
  ...      />
  ...   </ifrit:traversal_adapter>
  ... </configure>"""   
  >>> ignored = zcml_string(_TRAVERSAL_ZCML, context=context)
  >>> isinstance(ifrit.tests.traversalFactory, ElementTraversalAdapterFactory)
  True
  >>> len(ifrit.tests.traversalFactory.markers)
  1
  >>> ifrit.tests.traversalFactory.markers['items'] is IMarker
  True

We can then look up that factory as an adapter::

  >>> from zope.publisher.interfaces import IPublishTraverse
  >>> traverser = getAdapter(dummy, IPublishTraverse)
  >>> target = traverser.publishTraverse(None, 'items')
  >>> target.__parent__ is dummy
  True
  >>> target.__name__
  'items'
  >>> IMarker.providedBy(target)
  True

and as a view::

  >>> from zope.component import getMultiAdapter
  >>> traverser = getMultiAdapter((dummy, request), IPublishTraverse)
  >>> target = traverser.publishTraverse(request, 'items')
  >>> target.__parent__ is dummy
  True
  >>> target.__name__
  'items'
  >>> IMarker.providedBy(target)
  True

EOT::

  >>> del ifrit.tests.IDummy
  >>> del ifrit.tests.alternateFactory
  >>> tearDown()


# vim: syntax=rst
CVS: $Id: README.txt,v 1.8 2007/02/17 19:48:15 tseaver Exp $
