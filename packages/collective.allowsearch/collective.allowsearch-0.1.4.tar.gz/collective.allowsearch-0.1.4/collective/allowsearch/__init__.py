from zope import component

from Products.CMFPlone.CatalogTool import registerIndexableAttribute
from collective.allowsearch.interfaces import IAllowedRolesAndUsers

def allowedRolesAndUsers(obj, portal, **kwargs):
    """
    We reregister the 'allowedRolesAndUsers' attribute here to
    have a chance to extend the list the original returns. We
    have added a utility which provides the default (original)
    behavior, and use it here. Then we try to adapt the object
    to be indexed to IAllowedRolesAndUsers and try to use that.
    If we cannot adapt, then we use the original.
    """
    adapted = IAllowedRolesAndUsers(obj, None)
    if adapted is None:
        allowed = component.getUtility(IAllowedRolesAndUsers,u"collective.allowsearch.default")(obj,portal,**kwargs)
        return allowed

    return adapted(obj,portal,**kwargs)

registerIndexableAttribute( 'allowedRolesAndUsers', allowedRolesAndUsers)

def initialize(context):
    """Intializer called when used as a Zope 2 product."""
    pass
