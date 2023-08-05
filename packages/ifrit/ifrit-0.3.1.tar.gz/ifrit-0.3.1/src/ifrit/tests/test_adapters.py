import unittest
from StringIO import StringIO

from zope.interface import Interface
from zope.interface import implements
from zope.publisher.interfaces.browser import IBrowserRequest
from zope.app.testing.placelesssetup import PlacelessSetup
from zope.app.testing import ztapi

class OFSFileAsXMLTests(unittest.TestCase):

    def _getTargetClass(self):
        from ifrit.adapters import OFSFileAsXML
        return OFSFileAsXML

    def _makeOne(self, data):
        file = DummyFile(data)
        return self._getTargetClass()(file)

    def test_context_with_string_data(self):
        from ifrit.interfaces import IElement
        _STRING_PROFILE = """<?xml version="1.0"?><document/>"""
        adapted = self._makeOne(_STRING_PROFILE)
        buffer = StringIO()
        adapted.serialize(buffer)
        self.assertEqual(buffer.getvalue(), _STRING_PROFILE)

    def test_context_with_unicode_data(self):
        from ifrit.interfaces import IElement
        _UNICODE_PROFILE = u"""<?xml version="1.0"?><document/>"""
        adapted = self._makeOne(_UNICODE_PROFILE)
        buffer = StringIO()
        adapted.serialize(buffer)
        self.assertEqual(buffer.getvalue(), _UNICODE_PROFILE.encode('utf8'))

    def test_context_with_pdata_data(self):
        from ifrit.interfaces import IElement
        _PDATA_PROFILE = DummyPData('<?xml version="1.0"?>',
                                    DummyPData('<document/>'))
        adapted = self._makeOne(_PDATA_PROFILE)
        buffer = StringIO()
        adapted.serialize(buffer)
        self.assertEqual(buffer.getvalue(), '<?xml version="1.0"?><document/>')


class ElementMakerTests(unittest.TestCase, PlacelessSetup):

    def setUp(self):
        PlacelessSetup.setUp(self)

    def tearDown(self):
        PlacelessSetup.tearDown(self)

    def _makeOne(self, path=None, parser_name=None, multiple=False):
        from zope.interface import directlyProvides
        from ifrit.adapters import ElementMaker
        file = DummyFile()
        maker = ElementMaker(path, parser_name=parser_name, multiple=multiple)
        return maker(file)

    def _fakeSerializer(self, data):
        from ifrit.interfaces import IXMLSerialization
        class DummyAdapter:
            def __init__(self, context):
                pass
            def serialize(self, buffer):
                buffer.write(data)
        ztapi.provideAdapter(IDummy, IXMLSerialization, DummyAdapter, '')

    def _registerStreamParsers(self):
        from elementtree.ElementTree import parse as et_parse
        from ifrit.interfaces import IStreamParser
        from ifrit.lxml_utils import parse as lx_parse
        from ifrit.objectify_utils import parse as ob_parse
        ztapi.provideUtility(IStreamParser, et_parse, 'elementtree')
        ztapi.provideUtility(IStreamParser, lx_parse, 'lxml')
        ztapi.provideUtility(IStreamParser, ob_parse, 'objectify')

    def test_with_no_path_returns_root(self):
        from zope.interface.verify import verifyObject
        _PROFILE = '<?xml version="1.0"?><document><section/></document>'
        self._fakeSerializer(_PROFILE)
        self._registerStreamParsers()

        for parser_name in ('elementtree', 'lxml', 'objectify'):
            adapted = self._makeOne(path=None, parser_name=parser_name)
            self.assertEqual(adapted.tag, 'document')
            self.assertEqual(adapted.find('./section').tag, 'section')

    def test_with_path_returns_child(self):
        from zope.interface.verify import verifyObject
        _PROFILE = '<?xml version="1.0"?><document><section/></document>'
        self._fakeSerializer(_PROFILE)
        self._registerStreamParsers()
        adapted = self._makeOne(path='./section')
        self.assertEqual(adapted.tag, 'section')

    def test_with_invalid_path_returns_None(self):
        _PROFILE = '<?xml version="1.0"?><document><section/></document>'
        self._fakeSerializer(_PROFILE)
        self._registerStreamParsers()
        adapted = self._makeOne(path='./nonesuch')
        self.assertEqual(adapted, None)

    def test_with_path_and_multiple_returns_children(self):
        from zope.interface.verify import verifyObject
        _PROFILE = ('<?xml version="1.0"?>'
                    '<document>'
                     '<section/>'
                     '<section/>'
                    '</document>'
                   )
        self._fakeSerializer(_PROFILE)
        self._registerStreamParsers()
        adapted = self._makeOne(path='./section', multiple=True)
        self.assertEqual(len(adapted), 2)
        for node in adapted:
            self.assertEqual(node.tag, 'section')

class ElementTraversalAdapterTests(unittest.TestCase, PlacelessSetup):

    def setUp(self):
        PlacelessSetup.setUp(self)

    def tearDown(self):
        PlacelessSetup.tearDown(self)

    def _getTargetClass(self):
        from ifrit.adapters import ElementTraversalAdapter
        return ElementTraversalAdapter

    def _makeOne(self):
        from zope.interface import directlyProvides
        file = DummyFile()
        directlyProvides(file, IDummy)
        return self._getTargetClass()(file)

    def test_class_conforms_to__IPublishTraverse(self):
        from zope.interface.verify import verifyClass
        from zope.publisher.interfaces import IPublishTraverse
        verifyClass(IPublishTraverse, self._getTargetClass())

    def test_object_conforms_to_IPublishTraverse(self):
        from zope.interface.verify import verifyObject
        from zope.publisher.interfaces import IPublishTraverse
        from ifrit.interfaces import IElement
        verifyObject(IPublishTraverse, self._makeOne())

    def _makeElementAdapter_etree(self, context):
        from elementtree.ElementTree import XML
        return XML('<dummy><sub/></dummy>')

    def _makeElementAdapter_lxml(self, context):
        from ifrit.lxml_utils import fromstring
        return fromstring('<dummy><sub/></dummy>')

    def _makeElementAdapter_objectify(self, context):
        from ifrit.lxml_utils import fromstring
        return fromstring('<dummy><sub/></dummy>')

    def test_publishTraverse_with_good_name_returns_wrapped_element(self):
        from zope.interface import providedBy, directlyProvides
        from zope.interface.verify import verifyObject
        from zope.publisher.interfaces import IPublishTraverse
        from ifrit.interfaces import IElement

        class IMyElement(IElement):
            pass

        for name, adapter in (('objectify', self._makeElementAdapter_objectify),
                              ('lxml', self._makeElementAdapter_lxml),
                              ('etree', self._makeElementAdapter_etree),
                              ):
            ztapi.provideAdapter(IDummy, IElement, adapter, name)
            adapter = self._makeOne()
            request = {}

            node = adapter.publishTraverse(request, name)

            self.assertEqual(node.tag, 'dummy')
            self.assertEqual(node.__parent__, adapter.context)
            self.assertEqual(node.__name__, name)
            self.assertEqual(list(providedBy(node)), [])

            directlyProvides(node, IMyElement)
            self.failUnless(IMyElement.providedBy(node))

    def test_publishTraverse_with_bad_name_raises_NotFound(self):
        from zope.publisher.interfaces import NotFound
        from ifrit.interfaces import IElement

        ztapi.provideAdapter(IDummy, IElement,
                             self._makeElementAdapter_etree, 'name')
        adapter = self._makeOne()
        request = {}

        self.assertRaises(NotFound, adapter.publishTraverse, request, 'bad')

    def test_publishTraverse_falls_back_to_default(self):
        from zope.component import adapts
        from zope.component import provideAdapter
        from zope.publisher.interfaces.browser import IBrowserView
        from ifrit.interfaces import IElement

        class DummyView(object):
            implements(IBrowserView)
            adapts(IDummy, IBrowserRequest)
            def __init__(self, context, request):
                pass

        provideAdapter(DummyView, name='view.html')
        ztapi.provideAdapter(IDummy, IElement,
                             self._makeElementAdapter_etree, 'name')
        adapter = self._makeOne()
        request = DummyRequest()

        found = adapter.publishTraverse(request, 'view.html')

        self.failUnless(isinstance(found, DummyView))

class ElementTraversalAdapterFactoryTests(unittest.TestCase, PlacelessSetup):

    def setUp(self):
        PlacelessSetup.setUp(self)

    def tearDown(self):
        PlacelessSetup.tearDown(self)

    def _getTargetClass(self):
        from ifrit.adapters import ElementTraversalAdapterFactory
        return ElementTraversalAdapterFactory

    def _makeOne(self, markers):
        return self._getTargetClass()(markers)

    def _makeElementAdapter(self, context):
        #from elementtree.ElementTree import XML
        from ifrit.lxml_utils import fromstring
        return fromstring('<dummy><sub/></dummy>')

    def test___call__with_known_name_returns_marked_element(self):
        from ifrit.interfaces import IElement
        class IMarker(Interface):
            pass
        _MARKERS = {'known': IMarker}

        ztapi.provideAdapter(IDummy, IElement,
                            self._makeElementAdapter, 'known')

        factory = self._makeOne(_MARKERS)
        context = DummyFile()
        request = DummyRequest()
        adapter = factory(context, request)

        node = adapter.publishTraverse(request, 'known')

        self.failUnless(IMarker.providedBy(node))

    def test___call__with_unknown_name_returns_unmarked_element(self):
        from zope.interface import providedBy
        from ifrit.interfaces import IElement
        class IMarker(Interface):
            pass
        _MARKERS = {'known': IMarker}

        ztapi.provideAdapter(IDummy, IElement,
                            self._makeElementAdapter, 'other')

        factory = self._makeOne(_MARKERS)
        context = DummyFile()
        request = DummyRequest()
        adapter = factory(context, request)

        node = adapter.publishTraverse(request, 'other')

        self.assertEquals(len(list(providedBy(node))), 0)

class IDummy(Interface):
    pass

class DummyFile:
    implements(IDummy)
    def __init__(self, data=''):
        self.data = data

class DummyPData:
    def __init__(self, data, next=None):
        self.data = data
        self.next = next

class DummyRequest(object):
    implements(IBrowserRequest)

def test_suite():
    from zope.testing.doctest import DocFileTest
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(OFSFileAsXMLTests))
    suite.addTest(unittest.makeSuite(ElementMakerTests))
    suite.addTest(unittest.makeSuite(ElementTraversalAdapterTests))
    suite.addTest(unittest.makeSuite(ElementTraversalAdapterFactoryTests))
    suite.addTest(DocFileTest('README.txt', package='ifrit'))
    suite.addTest(DocFileTest('nodes_with_markers.txt', package='ifrit'))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')

