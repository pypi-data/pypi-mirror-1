from DateTime import DateTime

from zope.interface import implements
from zope.component import getUtility

from Products.CMFCore.utils import getToolByName
from Products.CMFCore.interfaces import ISiteRoot
from Products.ZCatalog.ZCatalog import ZCatalog
from Products.CMFCore.utils import _getAuthenticatedUser
from Products.CMFCore.utils import _checkPermission
from Products.CMFCore.permissions import AccessInactivePortalContent

from Products.AdvancedQuery import Eq, Between, Le, In

from ely.advancedquery.interfaces import IAdvancedCatalogQuery

class AdvancedCatalogQuery(object):

    implements(IAdvancedCatalogQuery)

    def __call__(self, query, sort_specs=(), show_inactive=False):
        """Calls ZCatalog.evalAdvancedQuery
        """
        portal = getUtility(ISiteRoot)
        catalog = getToolByName(portal, 'portal_catalog')
        user = _getAuthenticatedUser(catalog)
        query = query & In('allowedRolesAndUsers',
                           catalog._listAllowedRolesAndUsers(user))
        # this differs a little from the std CatalogTool where we omit
        # _checkPermission(AccessInactivePortalContent, catalog)
        if not show_inactive:
            now = DateTime()
            query = query & Le('effective', now, filter=True)
        return catalog.evalAdvancedQuery(query, sortSpecs=sort_specs)

