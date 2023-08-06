from zope.interface import Interface

class IAdvancedCatalogQuery(Interface):

    """
    A utility to use the Advanced Query extension to Zope's Zcatalog
    in a plone site.
    """

    def __call__(query):
        """
        execute the query on the portal catalog
        """
