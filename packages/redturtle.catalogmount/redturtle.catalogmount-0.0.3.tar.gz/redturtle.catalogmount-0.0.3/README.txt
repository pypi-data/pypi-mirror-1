======================
redturtle.catalogmount
======================

Overview
============

Small package which helps mount portal_catalog in separate ZODB. Install threw portal_quickinstaler.

This small package unpickles your existing portal_catalog and creates new mounting point in the new storage.

Instalation
============

* Add ``redturtle.catalogmount`` to the list of eggs to install, e.g.::

	[buildout]
	...
	eggs =
	...
	redturtle.catalogmount

* Add new storage for your zeo, e.g.::

	[zeoserver]
	recipe = plone.recipe.zope2zeoserver
	...
	zeo-conf-additional =
	<filestorage 2>
	path ${buildout:directory}/var/filestorage/CatalogData.fs
	</filestorage>

* And new mount-point for zeoclient, e.g.::	        

	[zeo-instance1]
	...
	zope-conf-additional =
	<zodb_db catalog>
	mount-point /plone/portal_catalog
	container-class Products.CMFPlone.CatalogTool.CatalogTool
	<zeoclient>
	server ${zeoserver:zeo-address}
	storage 2
	name catalogstorage
	var ${buildout:parts-directory}/instance1/var
	cache-size 400MB
	</zeoclient>
	</zodb_db>

where ``/plone/portal_catalog`` is the path to your portal_catalog.

* Re-run buildout, e.g. with::

    $ ./bin/buildout


Author & Contact
================

.. image:: http://www.slowfoodbologna.it/redturtle_logo.png

:Author: Andrew Mleczko <``andrew.mleczko@redturtle.net``>
 
**RedTurtle Technology** 

http://www.redturtle.net

