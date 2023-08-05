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
  >>> IElement.providedBy(d_node)
  True
  >>> d_node.text
  'testing'

Sigh, we can't pass ``name`` to an interface-call shortcut::

  >>> from zope.component import getAdapter
  >>> i_node = getAdapter(dummy, IElement, name='items')
  >>> i_node.tag
  'items'
  >>> IElement.providedBy(i_node)
  True

  >>> i_node = getAdapter(with_items, IElement, name='items')
  >>> sub = i_node.findall('item')
  >>> [x.text for x in sub]
  ['a', 'b']

We can arrange to have a different marker interface on the nodes::

  >>> class IMyElement(IElement):
  ...     pass
  >>> my_factory = ElementMaker(marker=IMyElement)
  >>> ztapi.provideAdapter(IDummy, IElement, my_factory, name='mine')
  >>> my_node = getAdapter(dummy, IElement, name='mine')
  >>> IMyElement.providedBy(my_node)
  True

Creating Path Adapters in ZCML
------------------------------

The package provides a custom ZCML directive which creates an adapter
factory::

  >>> import ifrit.tests
  >>> ifrit.tests.IDummy = IDummy
  >>> ifrit.tests.IMyElement = IMyElement
  >>> from zope.configuration.xmlconfig import file as zcml_file
  >>> from zope.configuration.xmlconfig import string as zcml_string
  >>> context = zcml_file('meta.zcml', package=ifrit)
  >>> _TEST_ZCML = """\
  ... <configure xmlns="http://namespaces.zope.org/zope"
  ...            xmlns:ifrit="http://namespaces.zope.org/ifrit">
  ...   <ifrit:path_adapter
  ...      for="ifrit.tests.IDummy"
  ...      name="alternate"
  ...      path="items"
  ...      parser_name="elementtree"
  ...      marker="ifrit.tests.IMyElement"
  ...      module="ifrit.tests"
  ...      factory_name="alternateFactory" />
  ... </configure>"""   
  >>> ignored = zcml_string(_TEST_ZCML, context=context)
  >>> isinstance(ifrit.tests.alternateFactory, ElementMaker)
  True
  >>> ifrit.tests.alternateFactory.path == 'items'
  True
  >>> adapter = getAdapter(dummy, IElement, name='alternate')
  >>> adapter.tag
  'items'
  >>> IElement.providedBy(adapter)
  True

EOT::

  >>> del ifrit.tests.IDummy
  >>> del ifrit.tests.IMyElement
  >>> del ifrit.tests.alternateFactory
  >>> tearDown()


CVS: $Id: README.txt,v 1.4 2007/02/09 21:41:42 tseaver Exp $
