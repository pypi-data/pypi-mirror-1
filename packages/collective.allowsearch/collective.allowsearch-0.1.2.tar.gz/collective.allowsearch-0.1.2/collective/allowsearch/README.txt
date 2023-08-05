collective.allowsearch
======================

:Author:    $Author: seletz $
:Date:      $Date: 2007-10-24 14:44:22 +0200 (Wed, 24 Oct 2007) $
:Revision:  $Revision: 52347 $

Abstract
--------

This package can be used to give users/roles in plone elevated rights on
ZCatalog searches. This is useful for sites where you want Anonymous users
to find content without them having the View permission.

Setup
-----

Test setup::

    >>> from zope import component
    >>> pw = self.portal.portal_workflow

We need some content to search for::

    >>> self.setRoles(("Manager",))
    >>> _ = self.folder.invokeFactory( "Document", "zonk" )
    >>> zonk = self.folder.get(_)
    >>> zonk.update( title="Zonk", description="zonk desc", text="My content" )
    >>> pw.doActionFor( zonk, "submit" )

Test Registry
-------------

For this stuff to work, we registered our own function with the
**CMFPlone** eioRegistry::

    >>> from Products.CMFPlone.CatalogTool import _eioRegistry
    >>> from collective.allowsearch import allowedRolesAndUsers
    >>> _eioRegistry["allowedRolesAndUsers"] == allowedRolesAndUsers
    True

Our registered function relies on a global utility, which we register, to
fetch the default behavior if needed. For that, we have a interface which
describes the utility::

    >>> from collective.allowsearch.interfaces import IAllowedRolesAndUsers

This interface just specifies that the utility is callable and takes the
same parameters as the default implementation in **CMFPlone**. So lets try
to fetch the default implementation::

    >>> component.getUtility(IAllowedRolesAndUsers, u"collective.allowsearch.default")
    <collective.allowsearch.utilities.DefaultAllowedRolesAndUsers object at ...>

Added behavior
--------------

To add our desired behavior, the newly registered **allowedRolesAndUsers**
function tries to adapt the object being indexed to
**IAllowedRolesAndUsers**. If such an adapter is found, then it's called
and the result is put into the **allowedRolesAndUsers** indes. If no such
adapter is found, then we look up the default behavior as an utility and
call that one. Thus we always fall back on the default behavior.

To be able to specify that a certain object is allowed for **Anonymous**
users to be found, we define a new marker interface::

    >>> from collective.allowsearch.interfaces import IAllowAnonymousSearchMarker

The idea is that we mark objects with this marker interface, then have and
adapter to **IAllowedRolesAndUsers** for all content objects and have this
adapter check for the marked interface in its **__call__** method. Lets try
that::

    >>> adapted = IAllowedRolesAndUsers(zonk)
    >>> "Anonymous" in adapted(zonk, self.portal)
    False

The content is in "pending" state, thus **Anonymous** users do not see it.
If we mark it with our marker interface things do change::

    >>> from zope.interface import alsoProvides
    >>> alsoProvides(zonk, IAllowAnonymousSearchMarker)
    >>> IAllowAnonymousSearchMarker.providedBy(zonk)
    True

the **Anonymous** role is now in added by the adapter::

    >>> adapted = IAllowedRolesAndUsers(zonk)
    >>> "Anonymous" in adapted(zonk, self.portal)
    True

We revert the mark for further testing::

    >>> from zope.interface import noLongerProvides
    >>> noLongerProvides(zonk, IAllowAnonymousSearchMarker)
    >>> zonk.reindexObject()

Test searches
-------------

Ok, now lets test if the catalog does return the brain and whether or not we
have **View** permissions as **Anonymous** or not.

First try if the content is in the catalog already::

    >>> pc = self.portal.portal_catalog
    >>> pc(SearchableText="Zonk")
    [<Products.ZCatalog.Catalog.mybrains object at ...>]

Mangle the roles we have, to be **Anonymous**. We should no longer see the
content::

    >>> self.logout()
    >>> pc(SearchableText="Zonk")
    []


::

 vim: set ft=rst tw=75 nocin nosi ai sw=4 ts=4 expandtab:
