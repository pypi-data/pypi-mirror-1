import logging, types
import transaction
from zope.interface import implements
from zope.component import getMultiAdapter
from zope.component import queryMultiAdapter

from Missing import MV
from Acquisition import aq_inner
from Acquisition import aq_parent

from Products.CMFCore.utils import getToolByName
from Products.ZCatalog.Catalog import safe_callable


try:
    from plone.indexer.interfaces import IIndexableObject
except ImportError:
    class IIndexableObject:pass
    from plone.app.content.interfaces import IIndexableObjectWrapper \
        as _old_IIndexableObjectWrapper
    from plone.app.content.interfaces import IIndexableObjectWrapper

    register_bbb_indexers = lambda:None

    IS_NEW = False
else:    
    from Products.CMFPlone.CatalogTool import register_bbb_indexers
    from Products.CMFPlone.CatalogTool import _old_IIndexableObjectWrapper

    IS_NEW = True


from quintagroup.catalogupdater.interfaces import ICatalogUpdater

LOG = logging.getLogger('quintagroup.catalogupdater')


class CatalogUpdaterUtility(object):

    implements(ICatalogUpdater)

    def validate(self, cat, cols):
        # Validate catalog and column name
        AVAIL_COLTYPES = list(types.StringTypes) + [types.ListType, types.TupleType]

        _cat = getattr(cat, '_catalog', None)
        if _cat is None:
            raise AttributeError("%s - is not ZCatalog based catalog" % cat)

        if not type(cols) in AVAIL_COLTYPES:
            raise TypeError("'columns' parameter must be one of the following " \
                "types: %s" % AVAIL_COLTYPES)
        # Normalize columns
        if type(cols) in types.StringTypes:
            cols = [cols,]
        # Check is every column present in the catalog
        for col in cols:
            if not _cat.schema.has_key(col):
                raise AttributeError("'%s' - not presented column in %s catalog " % (col, cat))

        return _cat, cols


    def getWrappedObjectNew(self, obj, portal, catalog):
        # Returned wrapped 'obj' object with IIndexable wrapper
        w = obj
        if not IIndexableObject.providedBy(obj):
             # BBB: Compatibility wrapper lookup. Should be removed in Plone 4.
             register_bbb_indexers()
             wrapper = queryMultiAdapter((obj, portal), _old_IIndexableObjectWrapper)
             if wrapper is not None:
                 w = wrapper
             else:
                 # This is the CMF 2.2 compatible approach, which should be used going forward
                 wrapper = queryMultiAdapter((obj, catalog), IIndexableObject)
                 if wrapper is not None:
                     w = wrapper
        return w


    def getWrappedObjectOld(self, obj, portal, catalog):
        # Returned wrapped 'obj' object with IIndexable wrapper
        wf = getattr(self, 'portal_workflow', None)
        # A comment for all the frustrated developers which aren't able to pin
        # point the code which adds the review_state to the catalog. :)
        # The review_state var and some other workflow vars are added to the
        # indexable object wrapper throught the code in the following lines
        if wf is not None:
            vars = wf.getCatalogVariablesFor(obj)
        else:
            vars = {}
        
        w = getMultiAdapter((obj, portal), _old_IIndexableObjectWrapper)
        w.update(vars)

        return w


    def updateMetadata4All(self, catalog, columns):
        """ Look into appropriate method of ICatalogUpdate interface
        """

        _catalog, columns = self.validate(catalog, columns)

        portal = getToolByName(catalog, 'portal_url').getPortalObject()
        root = aq_parent(portal)
        
        data = _catalog.data
        schema = _catalog.schema
        paths = _catalog.paths
        getWrappedObject = IS_NEW and self.getWrappedObjectNew or self.getWrappedObjectOld
        # For subtransaction support
        threshold = getattr(catalog, 'threshold', 10000)
        _v_total = 0
        _v_transaction = None

        # For each catalog record update metadata
        for rid, md in data.items():
            # get an object
            obj_uid = paths[rid]
            try:
                obj = root.unrestrictedTraverse(obj_uid)
                obj = getWrappedObject(obj, portal, catalog)
            except:
                LOG.error('updateMetadata4All could not resolve '
                          'an object from the uid %r.' % obj_uid)
                continue

            mdlist = list(md)
            for column in columns:
                # calculate the column value
                attr=getattr(obj, column, MV)
                if(attr is not MV and safe_callable(attr)): attr=attr()
                # Update metadata value
                indx = schema[column]
                mdlist[indx] = attr

            # Update catalog record
            data[rid] = tuple(mdlist)

            # Steeled from ZCatalog
            if threshold is not None:
                # figure out whether or not to commit a subtransaction.
                t = id(transaction.get())
                if t != _v_transaction:
                    _v_total = 0
                _v_transaction = t
                _v_total = _v_total + 1
                if _v_total > threshold:
                    transaction.savepoint(optimistic=True)
                    catalog._p_jar.cacheGC()
                    _v_total = 0
                    LOG.info('commiting subtransaction')

