A utility that wraps up the Advanced Query extension to ZCatalog (see
http://www.dieter.handshake.de/pyprojects/zope/AdvancedQuery.html)

    >>> from Products.AdvancedQuery import Eq, Between, Le, MatchGlob, \
    ...      RankByQueries_Sum
    >>> from zope.component import getUtility
    >>> from pprint import pprint
    >>> from ely.advancedquery.interfaces import IAdvancedCatalogQuery
    >>> advancedquery = getUtility(IAdvancedCatalogQuery)

    We need to monkey with the portal catalog to give it enough
    features to resolve urls

    Make some content up

    >>> folder = self.folder

    >>> _ = folder.invokeFactory('Folder', 'folder1', title='Folder 1')
    >>> _ = folder.invokeFactory('Folder', 'folder2', title='Folder 2')
    >>> _ = folder.invokeFactory('Folder', 'folder3', title='Folder 3')
    >>> folder1 = folder.folder1
    >>> folder2 = folder.folder2
    >>> folder3 = folder.folder3

    >>> _ = folder1.invokeFactory('Document', 'animals1', title='All about animals')
    >>> _ = folder1.invokeFactory('Document', 'animals2', title='All about fish')
    >>> _ = folder2.invokeFactory('Document', 'bread1', title='All about bread')
    >>> _ = folder2.invokeFactory('Document', 'bread2', title='All about rye bread')
    >>> _ = folder3.invokeFactory('Document', 'ocean1', title='All about ocean')
    >>> _ = folder3.invokeFactory('Document', 'ocean2', title='All about waves')

    >>> query = Eq('portal_type', 'Document')
    >>> results = advancedquery(query)
    >>> ids = [x.getId for x in results]
    >>> ids.sort()
    >>> pprint(ids)
    ['animals1', 'animals2', 'bread1', 'bread2', 'front-page', 'ocean1', 'ocean2']

    >>> query = Eq('portal_type','Document') & MatchGlob('Title','animal*')
    >>> results = advancedquery(query)
    >>> ids = [x.getId for x in results]
    >>> pprint(ids)
    ['animals1']

    >>> query = Eq('portal_type','Document') & Eq('SearchableText','about')
    >>> results = advancedquery(query)
    >>> ids = [x.getId for x in results]
    >>> ids.sort()
    >>> pprint(ids)
    ['animals1', 'animals2', 'bread1', 'bread2', 'front-page', 'ocean1', 'ocean2']

    >>> query = Eq('portal_type','Document') & Eq('SearchableText','animal')
    >>> results = advancedquery(query)
    >>> ids = [x.getId for x in results]
    >>> pprint(ids)
    []

    Yum, globbing

    >>> query = Eq('portal_type','Document') & Eq('SearchableText','animal*')
    >>> results = advancedquery(query)
    >>> ids = [x.getId for x in results]
    >>> ids.sort()
    >>> pprint(ids)
    ['animals1', 'animals2']


    advancedquery supports effective dates fine

    >>> from DateTime import DateTime
    >>> plone_utils = self.portal.plone_utils
    >>> plone_utils.editMetadata(folder2.bread2, effective_date='2010-01-01')
    >>> folder2.bread2.reindexObject()
    >>> query = Eq('portal_type', 'Document')
    >>> results = advancedquery(query)
    >>> ids = [x.getId for x in results]
    >>> ids.sort()
    >>> pprint(ids)
    ['animals1', 'animals2', 'bread1', 'front-page', 'ocean1', 'ocean2']


    >>> self.logout()
    >>> query = Eq('portal_type', 'Document')
    >>> results = advancedquery(query)
    >>> ids = [x.getId for x in results]
    >>> ids.sort()
    >>> pprint(ids)
    ['front-page']

    Now publish some of them and see what we get

    First login and make sure we can still see them all

    >>> self.login()
    >>> query = Eq('portal_type', 'Document')
    >>> results = advancedquery(query, show_inactive=True)
    >>> ids = [x.getId for x in results]
    >>> ids.sort()
    >>> pprint(ids)
    ['animals1', 'animals2', 'bread1', 'front-page', 'ocean1', 'ocean2']

    The brain objects of these results don't get a REQUEST object, I'm
    not sure why, but here is a workaround for getURL

    >>> urls = [self.app.REQUEST.physicalPathToURL(x.getPath()) for x in results]
    >>> urls.sort()
    >>> pprint(urls)
    ['http://nohost/plone/Members/test_user_1_/folder1/animals1',
     'http://nohost/plone/Members/test_user_1_/folder1/animals2',
     'http://nohost/plone/Members/test_user_1_/folder2/bread1',
     'http://nohost/plone/Members/test_user_1_/folder3/ocean1',
     'http://nohost/plone/Members/test_user_1_/folder3/ocean2',
     'http://nohost/plone/front-page']



    Publish the unpublished ones

    >>> workflow_tool = self.portal.portal_workflow
    >>> items = [x.getObject() for x in results]
    >>> for item in items:
    ...     if workflow_tool.getInfoFor(item, 'review_state') == 'private':
    ...         workflow_tool.doActionFor(item, 'submit')
    ...         self.setRoles(['Reviewer'])
    ...         workflow_tool.doActionFor(item, 'publish')

    Go back to anonymous

    >>> self.logout()
    >>> query = Eq('portal_type', 'Document')
    >>> results = advancedquery(query)
    >>> ids = [x.getId for x in results]
    >>> ids.sort()
    >>> pprint(ids)
    ['animals1', 'animals2', 'bread1', 'front-page', 'ocean1', 'ocean2']

    Note how the effective date is still working


    Ranking

    We will rank by matching some term to searchable text

    >>> rankspec = RankByQueries_Sum(
    ...     (Eq('SearchableText', 'animals'),1),
    ...     (Eq('SearchableText', 'bread'),10),
    ...     )

    >>> query = Eq('portal_type', 'Document') & \
    ...         (Eq('SearchableText','animals') | \
    ...          Eq('SearchableText','bread'))
    >>> results = advancedquery(query, sort_specs=(rankspec,))
    >>> ids = [x.getId for x in results]
    >>> pprint(ids)
    ['bread1', 'animals1']

    >>> rankspec = RankByQueries_Sum(
    ...     (Eq('SearchableText', 'animals'),1),
    ...     (Eq('SearchableText', 'ocean'),5),
    ...     (Eq('SearchableText', 'bread'),10),
    ...     )

    >>> query = Eq('portal_type', 'Document')
    >>> results = advancedquery(query, sort_specs=(rankspec,))
    >>> ids = [x.getId for x in results]
    >>> pprint(ids)
    ['bread1', 'ocean1', 'animals1', '...', '...', '...']
