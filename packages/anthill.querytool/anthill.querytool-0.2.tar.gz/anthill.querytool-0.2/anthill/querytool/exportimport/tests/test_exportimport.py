import unittest, sys
from Testing import ZopeTestCase

from Products.Five import zcml
from zope.component import getMultiAdapter

from Products.GenericSetup.interfaces import IBody
from Products.GenericSetup.testing import BodyAdapterTestCase
from Products.GenericSetup.testing import DummySetupEnviron


_QBODY = """\
<?xml version="1.0"?>
<object name="query_tool" meta_type="QueryTool"> 
 <query name="searchAllAuthors"    
    catalog="portal_catalog">And(Eq("SearchableText", "$input*", Eq("Title", "$input*"))</query>
</object>
"""

class QueryToolXMLTests(BodyAdapterTestCase):

    def _getTargetClass(self):
        from Products.QueryTool.exportimport.exportimport import QueryToolXMLAdapter
        return QueryToolXMLAdapter

    def _populate(self, obj):
        obj.createPredefinedQueryFromString('searchAllAuthors', 'And(Eq("SearchableText", "$input*", Eq("Title", "$input*"))')

    def setUp(self):
        import Products.QueryTool
        from Products.QueryTool.QueryTool import QueryTool

        BodyAdapterTestCase.setUp(self)
        zcml.load_config('configure.zcml', Products.QueryTool)

        self._obj = QueryTool('query_tool')
        self._BODY = _QBODY

    def testExportContent(self):
        self._populate(self._obj)
        context = DummySetupEnviron()
        adapted = getMultiAdapter((self._obj, context), IBody)

def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(QueryToolXMLTests),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
