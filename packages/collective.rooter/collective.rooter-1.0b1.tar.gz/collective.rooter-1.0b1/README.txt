Introduction
============

This package adds a patch to Plone to ensure that call catalog queries are
'rooted' to the current navigation root (as defined by the INavigationRoot
interface). When installed, all catalog queries will have an implicit 'path'
parameter that limits search results to within the current navigation root,
unless a 'path' parameter is explicitly provided. This avoids "leakage" of
search results, portlet listings and the like.

In this context, the navigation root must be:

 * A folderish object
 * That provides the INavigationRoot marker interface
 * And is a "component site" in the Zope 3 Component Architecture sense
 
The 'collective.lineage' product provides a user friendly way to create such
types.

The navigation root will be kept as a thread local variable, in the same way
that the component site is accessible via the global `getSite()` function.
To get hold of the current traversed-over navigation root, you can use::

  from collective.rooter import getNavigationRoot
  
  current_root = getNavigationRoot()
  
The root may be None if no INavigationRoot has been traversed over.
