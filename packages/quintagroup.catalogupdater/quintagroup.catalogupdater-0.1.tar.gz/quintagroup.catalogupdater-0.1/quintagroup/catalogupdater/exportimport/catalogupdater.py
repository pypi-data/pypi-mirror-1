"""Catalog tool columns updater setup handlers.
"""
from zope.component import adapts
from zope.component import queryUtility

from Products.ZCatalog.interfaces import IZCatalog
from Products.GenericSetup.interfaces import ISetupEnviron
from Products.GenericSetup.ZCatalog.exportimport import ZCatalogXMLAdapter

from quintagroup.catalogupdater.interfaces import ICatalogUpdater


class CatalogUpdaterXMLAdapter(ZCatalogXMLAdapter):
    """XML im- and exporter for ZCatalog with
       support of columns updates
    """

    adapts(IZCatalog, ISetupEnviron)

    def _initColumns(self, node):
        super(CatalogUpdaterXMLAdapter, self)._initColumns(node)

        updatecols = []
        for child in node.childNodes:
            if child.nodeName != 'column':
                continue
            col = str(child.getAttribute('value'))
            if child.hasAttribute('update'):
                # Add the column to update list if it is there
                if col in self.context.schema()[:]:
                    updatecols.append(col)
                continue

        # Update columns in catalog
        if len(updatecols) > 0:
            catalog = self.context

            self._logger.info('Updating %s columns for %s Catalog.' % (
                updatecols, '/'.join(catalog.getPhysicalPath())) )

            cu = queryUtility(ICatalogUpdater, name='catalog_updater')
            cu.updateMetadata4All(catalog, updatecols)
