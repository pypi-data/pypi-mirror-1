collective.recipe.zope2cluster
==============================

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
