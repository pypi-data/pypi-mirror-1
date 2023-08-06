quintagroup.catalogupdater package is intended for extending ZCatalog API
with possiblity to update selected columns only. This package registers
'catalog_updater' utility for that.

To simplify usage of the utility, quintagroup.catalogupdater extends GenericSetup's
ZCatalog XMLAdapter handler, which allows to *update* attribute usage in *column* 
tag of *catalog.xml* file.

So, when you add a new column to the catalog, you add catalog.xml file
in some profile with following part::

 ...
 <column value="new_column" />
 ...

This adds *new_column* metadata to the portal_catalog, BUT, this
metadata will be empty untill you rebuild the catalog. To automate
this step you can add 'update="True"' attribute to the tag. And this
will lead to column update after adding. Thus, result usage should look
like this::

 ...
 <column value="new_column" update="True" />
 ...

It also supports subtransactions, based on threshold property of ZCatalog.

Installation
------------

See docs/INSTALL.txt file within product package for instructions.

Requirements
------------

* Plone 3.x

Author
------

* Andriy Mylenkyi


Copyright (c) "Quintagroup": http://quintagroup.com, 2004 - 2010
