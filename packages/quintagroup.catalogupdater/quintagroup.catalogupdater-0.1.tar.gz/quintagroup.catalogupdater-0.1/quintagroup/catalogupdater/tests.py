import unittest
import transaction

from zope.interface import Interface
from zope.component import queryUtility
from zope.component import provideAdapter

from Testing import ZopeTestCase as ztc

from Products.Five import zcml
from Products.Five import fiveconfigure
from Products.CMFCore.utils import getToolByName
from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import PloneSite
from Products.Archetypes.tests.utils import makeContent

from quintagroup.catalogupdater.utility import ICatalogUpdater

try:
    from plone.indexer.decorator import indexer
except ImportError:
    IS_NEW = False
    from Products.CMFPlone.CatalogTool import registerIndexableAttribute
else:
    IS_NEW = True


class TestCase(ptc.PloneTestCase):
    class layer(PloneSite):
        @classmethod
        def setUp(cls):
            import quintagroup.catalogupdater
            fiveconfigure.debug_mode = True
            zcml.load_config('configure.zcml', quintagroup.catalogupdater)
            fiveconfigure.debug_mode = False

ptc.setupPloneSite()

class TestUtility(TestCase):

    def afterSetUp(self):
        self.loginAsPortalOwner()
        self.my_doc = makeContent(self.portal, portal_type='Document', id='my_doc')
        self.catalog = getToolByName(self.portal, 'portal_catalog')
        self.logout()

        if IS_NEW:
            self.addIndexerNew()
        else:
            self.addIndexerOld()
        self.catalog.addColumn('test_column')


    def addIndexerNew(self):
        @indexer(Interface)
        def test_column(obj):
            return obj.id
        provideAdapter(test_column, name='test_column')


    def addIndexerOld(self):
        def test_column(obj, portal, **kwargs):
            return obj.id
        registerIndexableAttribute("test_column", test_column)


    def testSingleColumnUpdate(self):
        """ Test is metadata column updated with utility
        """
        mydoc = self.catalog.unrestrictedSearchResults(id='my_doc')[0]
        self.assertFalse(mydoc.test_column == 'my_doc',
            "'test_column' metadata updated in catalog " \
            "before utility call: '%s'" % mydoc.test_column)

        cu = queryUtility(ICatalogUpdater, name="catalog_updater")
        cu.updateMetadata4All(self.catalog, 'test_column')

        mydoc = self.catalog.unrestrictedSearchResults(id='my_doc')[0]
        self.assertTrue(mydoc.test_column == 'my_doc',
            "'test_column' metadata has wrong metadata in catalog: " \
            "'%s'" % mydoc.test_column)

    def testOnlyPointedColumnUpdate(self):
        """ Update a title property for the my_doc object
            (without reindexing) then, after utility usage
            - check is that metadata is leave unchanged.
        """
        self.loginAsPortalOwner()
        self.my_doc.update(title="My document")
        self.logout()

        mydoc = self.catalog.unrestrictedSearchResults(id='my_doc')[0]
        self.assertTrue(mydoc.Title == "My document", mydoc.Title)

        self.my_doc.setTitle('New my document') # catalog not updated
        cu = queryUtility(ICatalogUpdater, name="catalog_updater")
        cu.updateMetadata4All(self.catalog, 'test_column')

        mydoc = self.catalog.unrestrictedSearchResults(id='my_doc')[0]
        self.assertTrue(mydoc.Title == 'My document',
            "Other metadata updated: Title='%s'" % mydoc.Title)


    def testAllRecordsUpdate(self):
        """ Test is all records in catalog updated with utility
        """
        cu = queryUtility(ICatalogUpdater, name="catalog_updater")
        cu.updateMetadata4All(self.catalog, 'test_column')

        num_recs = len(self.catalog._catalog.data)
        allcat = self.catalog.unrestrictedSearchResults(path='/')
        num_updated = sum([1 for b in allcat if b.test_column==b.id])

        self.assertTrue(num_updated == num_recs, "Only %d records updated, " \
            "must be - %d" % (num_updated, num_recs))


    def testTransaction(self):
        """ Test is commited subtransactions
        """
        # savepoint patch
        global sp_commits
        sp_commits = 1 # Starts from 1 to count last commit
        orig_trsp = transaction.savepoint
        def dummy_savepoint(*args, **kwargs):
            global sp_commits
            sp_commits += 1
            orig_trsp(*args, **kwargs)
        transaction.savepoint = dummy_savepoint

        # set threshold for catalog
        num_recs = len(self.catalog.unrestrictedSearchResults(path='/'))
        num_subcommits = 3
        self.catalog.threshold = num_recs/num_subcommits

        cu = queryUtility(ICatalogUpdater, name="catalog_updater")
        cu.updateMetadata4All(self.catalog, 'test_column')

        self.assertTrue(sp_commits == num_subcommits,
            "Wrong number of transaction subcommits: actual:%d, must be: %d" % (
            sp_commits, num_subcommits))

        transaction.savepoint = orig_trsp
        


def test_suite():
    return unittest.TestSuite([
        unittest.makeSuite(TestUtility),
        ])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
