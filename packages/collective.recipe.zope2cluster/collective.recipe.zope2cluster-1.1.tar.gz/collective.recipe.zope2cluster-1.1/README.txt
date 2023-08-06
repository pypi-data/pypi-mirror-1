collective.recipe.zope2cluster
==============================

NOTE: This recipe is no longer needed as of zc.buildout 1.4.

Using zc.buildout to do the same thing
======================================

As of zc.buildout 1.4 you can create macros out of sections. This means that
you do not need this recipe anymore.

The following::

  [instance2]
  recipe = collective.recipe.zope2cluster
  instance-clone = instance
  http-address = 8081

Would become::

  [instance2]
  <= instance
  http-address = 8081

Here is a complete example::

  [buildout]
  parts =
     instance
     instance2
  
  extends = http://dist.plone.org/release/3.3/versions.cfg
  versions = versions
  
  [versions]
  zc.buildout = 1.4.1
  
  [zope2]
  recipe = plone.recipe.zope2install
  url = ${versions:zope2-url}
  
  [instance]
  recipe = plone.recipe.zope2instance
  user = admin:admin
  zope2-location = ${zope2:location}
  http-address = 8080
  
  [instance2]
  <= instance
  http-address = 8081

Using this recipe
=================

This recipe aims to make it easier to set up a cluster of zope clients.
The zope2cluster recipe allows us to point to an existing 
plone.recipe.zope2instance part and copy it's options.  Any options we define
in the zope2cluster part override the original instance's options.

Example::

  [instance]
  recipe = plone.recipe.zope2instance
  user = admin:admin
  http-address = 8080
  
  [instance2]
  recipe = collective.recipe.zope2cluster
  instance-clone = instance
  http-address = 8081

Our instance2 part ends up being an exact copy of instance but changes the
http-address to 8081.
