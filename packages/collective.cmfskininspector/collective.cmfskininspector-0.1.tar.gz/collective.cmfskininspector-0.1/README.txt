collective.cmfskininspector Package Readme
==========================================

Overview
--------

collective.cmfskininspector allows you to see all skin parts in all CMF skin
layers at once. This helps to found overwrites of templates etc.

To use it just get the inspect-cmf-skins view on your portal root, like
http://localhost:8080/portal/@@inspect-cmf-skins

To install it you need to add the collective.cmfskininspector egg and add a
zcml slug to load it's configure.zcml. With buildout and the zope2instance
recipe you can just add "zcml = collective.cmfskininspector" to the instance
part.
