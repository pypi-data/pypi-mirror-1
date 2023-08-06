import unittest
#import Testing

#from zope.interface import implements
from zope.component import getMultiAdapter
from zope.component import provideUtility

from Products.Five import zcml
from Products.GenericSetup.interfaces import IBody
from Products.GenericSetup.ZCatalog.tests import test_exportimport

from Products.GenericSetup.testing import DummyLogger
from Products.GenericSetup.testing import DummySetupEnviron

from quintagroup.catalogupdater.interfaces import ICatalogUpdater

_CATALOG_BODY = test_exportimport._CATALOG_BODY
_ZCTEXT_XML = test_exportimport._ZCTEXT_XML

_CATALOG_UPDATE_BODY = """\
<?xml version="1.0"?>
<object name="foo_catalog">
 <object name="foo_vocabulary" remove="True"/>
 <index name="foo_text" remove="True"/>
 <index name="foo_text" meta_type="ZCTextIndex">
  <indexed_attr value="foo_text"/>
  <extra name="index_type" value="Okapi BM25 Rank"/>
  <extra name="lexicon_id" value="foo_plexicon"/>
 </index>
 <index name="non_existing" remove="True"/>
 <column value="non_existing" remove="True"/>
 <column value="bacon" remove="True"/>
 <column value="eggs" update="True"/>
 <column value="spam" update="True"/>
</object>
"""


class DummyCatalogUpdaterUtility:
    _logger = None

    def updateMetadata4All(self, catalog, columns):
        self._logger.info("%s:%s" % (catalog.id, columns))
    

class CatalogUpdaterZCMLLayer(test_exportimport.ZCatalogXMLAdapterTests.layer):

    @classmethod
    def setUp(cls):
        # Not import 'configure.zcml' - because it register 'catalog_updater'
        # utility, which we override with DummyCatalogUpdaterUtility
        test_exportimport.ZCatalogXMLAdapterTests.layer.setUp()
        import quintagroup.catalogupdater
        zcml.load_config('overrides.zcml', quintagroup.catalogupdater)


class CatalogUpdaterXMLAdapterTest(test_exportimport.ZCatalogXMLAdapterTests):

    layer = CatalogUpdaterZCMLLayer

    def _getTargetClass(self):
        from quintagroup.catalogupdater.exportimport.catalogupdater import CatalogUpdaterXMLAdapter
        return CatalogUpdaterXMLAdapter

    def setUp(self):
        super(CatalogUpdaterXMLAdapterTest, self).setUp()

        self.logger = DummyLogger('CatalogUpdaterLogger', [])
        dummy_cu = DummyCatalogUpdaterUtility()
        dummy_cu._logger = self.logger
        provideUtility(dummy_cu, ICatalogUpdater, name="catalog_updater")

    def getLastMessage(self):
        messages = getattr(self.logger, '_messages', [])
        return messages[-1] or [None,]*3

    def test_body_set_update(self):
        # Assert that the catalog ends up the way we expect it to.
        self._populate_special(self._obj)
        context = DummySetupEnviron()
        context._should_purge = False
        adapted = getMultiAdapter((self._obj, context), IBody)
        adapted.body = _CATALOG_UPDATE_BODY
        self.assertEqual(adapted.body, _CATALOG_BODY % ('', _ZCTEXT_XML, ''))

        message = self.getLastMessage()
        self.assertEqual( message[-1], "foo_catalog:['eggs', 'spam']",
            "Not updated columns in catalog" )

def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(CatalogUpdaterXMLAdapterTest),
        ))

if __name__ == '__main__':
    from Products.GenericSetup.testing import run
    run(test_suite())
