import unittest
from StringIO import StringIO

from zope.interface import Interface
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
        _STRING_PROFILE = """<?xml version="1.0"?><profile/>"""
        adapted = self._makeOne(_STRING_PROFILE)
        buffer = StringIO()
        adapted.serialize(buffer)
        self.assertEqual(buffer.getvalue(), _STRING_PROFILE)

    def test_context_with_unicode_data(self):
        from ifrit.interfaces import IElement
        _UNICODE_PROFILE = u"""<?xml version="1.0"?><profile/>"""
        adapted = self._makeOne(_UNICODE_PROFILE)
        buffer = StringIO()
        adapted.serialize(buffer)
        self.assertEqual(buffer.getvalue(), _UNICODE_PROFILE.encode('utf8'))

    def test_context_with_pdata_data(self):
        from ifrit.interfaces import IElement
        _PDATA_PROFILE = DummyPData('<?xml version="1.0"?>',
                                    DummyPData('<profile/>'))
        adapted = self._makeOne(_PDATA_PROFILE)
        buffer = StringIO()
        adapted.serialize(buffer)
        self.assertEqual(buffer.getvalue(), '<?xml version="1.0"?><profile/>')


class ElementMakerTests(unittest.TestCase, PlacelessSetup):

    def setUp(self):
        PlacelessSetup.setUp(self)

    def tearDown(self):
        PlacelessSetup.tearDown(self)

    def _makeOne(self, path=None, parser_name=None):
        from zope.interface import directlyProvides
        from ifrit.adapters import ElementMaker
        file = DummyFile()
        directlyProvides(file, IDummy)
        return ElementMaker(path, parser_name=parser_name)(file)

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

    def test_with_no_path_provides_IElement(self):
        from zope.interface.verify import verifyObject
        from ifrit.interfaces import IElement
        _PROFILE = '<?xml version="1.0"?><profile><education/></profile>'
        self._fakeSerializer(_PROFILE)
        self._registerStreamParsers()

        for parser_name in ('elementtree', 'lxml', 'objectify'):
            adapted = self._makeOne(path=None, parser_name=parser_name)
            verifyObject(IElement, adapted)
            self.assertEqual(adapted.tag, 'profile')
            self.assertEqual(adapted.find('./education').tag, 'education')

    def test_with_path_provides_IElement(self):
        from zope.interface.verify import verifyObject
        from ifrit.interfaces import IElement
        _PROFILE = '<?xml version="1.0"?><profile><education/></profile>'
        self._fakeSerializer(_PROFILE)
        self._registerStreamParsers()
        adapted = self._makeOne(path='./education')
        verifyObject(IElement, adapted)
        self.assertEqual(adapted.tag, 'education')

    def test_with_invalid_path_returns_None(self):
        _PROFILE = '<?xml version="1.0"?><profile><education/></profile>'
        self._fakeSerializer(_PROFILE)
        self._registerStreamParsers()
        adapted = self._makeOne(path='./nonesuch')
        self.assertEqual(adapted, None)

class IDummy(Interface):
    pass

class DummyFile:
    def __init__(self, data=''):
        self.data = data

class DummyPData:
    def __init__(self, data, next=None):
        self.data = data
        self.next = next

def test_suite():
    from zope.testing.doctest import DocFileTest
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(OFSFileAsXMLTests))
    suite.addTest(unittest.makeSuite(ElementMakerTests))
    suite.addTest(DocFileTest('README.txt', package='ifrit'))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')

