from OFS.SimpleItem import SimpleItem

import Globals

from zope.interface import implements, Interface

from Acquisition import aq_inner
from AccessControl import ClassSecurityInfo
from OFS.SimpleItem import SimpleItem
from OFS.PropertyManager import PropertyManager
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

from Products.CMFCore import permissions as CMFCorePermissions
from Products.CMFCore.utils import UniqueObject, getToolByName

from config import *
from Query import Query

VM = 'View management screens'

class IQueryTool(Interface):
    """ Interface for query tool """

class QueryTool( UniqueObject, SimpleItem, PropertyManager ):
    """
    Tool that enables you to yield queries
    to the specified catalog over AdvancedSearch.
    """

    implements(IQueryTool)

    # fake for showing up in zmi tree
    isPrincipiaFolderish = 1

    id = TOOL_ID
    meta_type = portal_type = META_TYPE

    security = ClassSecurityInfo()

    manage_options = (
            {'label' : 'Submit query', 'action' : 'manage_submit_query'},
            {'label' : 'Predefined queries', 'action' : 'manage_predefined_queries'},
            ) + PropertyManager.manage_options + SimpleItem.manage_options

    security.declareProtected(CMFCorePermissions.ManagePortal, 'manage_submit_query')
    manage_submit_query = PageTemplateFile('www/submit_query', globals())

    security.declareProtected(CMFCorePermissions.ManagePortal, 'manage_predefined_queries')
    manage_predefined_queries = PageTemplateFile('www/predefined_queries', globals())
            
    def __init__(self, *args, **kwargs):

        # set default plone catalog
        self._query_history = []
        self._predefined_queries = {}
        self.setCatalog('portal_catalog')
        self._setProperty('linkmanager', '')

        try:
            self._setProperty('title', 'Query Tool')
        except:
            pass

    def getLinkManagerObject(self):
        """ Returns the associated link manager """

        if self.linkmanager:
            return self.unrestrictedTraverse(self.linkmanager)
       
        return None
            
    security.declareProtected(VM, 'setCatalog')
    def setCatalog(self, catalog_name):
        """ Sets the catalog for searching """

        self._setProperty('catalog', catalog_name)
        
    security.declarePublic('getCatalogName')
    def getCatalogName(self):
        """ Returns associated catalog """

        return self.catalog

    security.declarePublic('getCatalogObject')
    def getCatalogObject(self):
        """ Returns the catalog object """

        return getToolByName(self, self.getCatalogName())

    security.declarePublic('getCatalogIndizes')
    def getCatalogIndizes(self):
        """ Returns the indizes defined on catalog """

        return self.getCatalogObject().indexes()
        
    security.declareProtected(VM, 'appendQueryToHistory')
    def appendQueryToHistory(self, querystring):
        """ Appends query to history """

        self._query_history.insert(0, querystring)
        self._p_changed = 1
        
    security.declarePublic('getQueryHistory')
    def getQueryHistory(self):
        """ Returns all saved queries """
        
        return self._query_history

    security.declareProtected(VM, 'clearQueryHistory')
    def clearQueryHistory(self):
        """ Completely clears query history """

        self._query_history = []

    security.declareProtected(VM, 'setPredefinedQuery')
    def setPredefinedQuery(self, name, query):
        """ Saves the predefined query """

        self._predefined_queries[name] = query
        self._p_changed = 1

    security.declareProtected(VM, 'savePredefinedQueries')
    def savePredefinedQueries(self, names, catalogs, checks, querystrings, REQUEST=None):
        """ Edits multiple predefined queries """

        self._predefined_queries = {}
        for c in range(len(names)):
            self.createPredefinedQueryFromString(names[c], 
                            querystrings[c], catalogs[c], checks[c], REQUEST=None)

        if REQUEST:
            return REQUEST.RESPONSE.redirect(REQUEST['HTTP_REFERER'])

    security.declareProtected(VM, 'createPredefinedQueryFromString')
    def createPredefinedQueryFromString(self, name, querystring, catalog, check, REQUEST=None):
        """ Creates a predefined query fomr the given string """

        if name and querystring and catalog:
            query = Query(name).createFromString(querystring)
            query.setWrapSecurity(check)
            query.setCatalog(catalog)
            self.setPredefinedQuery(name, query)

        if REQUEST:
            return REQUEST.RESPONSE.redirect(REQUEST['HTTP_REFERER'])

    security.declareProtected(VM, 'setCachingEnabledFor')
    def setCachingEnabledFor(self, name, enabled = True):
        """ Sets the cache of the given query """

        query = self.getPredefinedQuery(name)
        query.setCachingEnabled(enabled)

    security.declareProtected(VM, 'deletePredefinedQuery')
    def deletePredefinedQuery(self, name, REQUEST=None):
        """ Removes the predefined query """

        if self._predefined_queries.has_key(name):
            del self._predefined_queries[name]
            self._p_changed = 1
            
        else:
            raise Exception, 'Could not find predefined query %s' % name

        if REQUEST:
            return REQUEST.RESPONSE.redirect(REQUEST['HTTP_REFERER'])

    security.declarePublic('getPredefinedQuery')
    def getPredefinedQuery(self, name):
        """ Returns the query object """

        if self._predefined_queries.has_key(name):
            return self._predefined_queries[name]

        else:
            raise Exception, 'Predefined query %s does not exist!' % name

    security.declareProtected(VM, 'getAllPredefinedQueries')
    def getAllPredefinedQueries(self):
        """ Returns all predefined query objects """

        return self._predefined_queries.values()

    security.declarePublic('executePredefinedQuery')
    def executePredefinedQuery(self, name, **kw):
        """ Executes the predefined query and returns the resultset. The catalog
        is taken from the Query.
        
        If you want to apply sorting then pass a parameter like the following:
        sort_on_filter = (('<fieldname>', 'asc|desc'), )
        """

        pq = self.getPredefinedQuery(name)
        catalog = getToolByName(self, pq.getCatalog())
        return pq.execute(context=aq_inner(self), catalog=catalog, **kw)

    security.declarePublic('executeStringQuery')
    def executeStringQuery(self, querystring, **kw):
        """ Takes a string and executes the contained query """
    
        # construct query on the fly - remember: Cache is disabled
        query = Query('instant_query').createFromString(querystring)
        
        self.appendQueryToHistory(querystring)
        return query.execute(context=aq_inner(self), catalog=self.getCatalogObject(), **kw)

    security.declareProtected(VM, 'manage_executeStringQuery')
    def manage_executeStringQuery(self, querystring, **kw):
        """ Resolve objects """

        ret = """<a href="%s/manage_submit_query">Back to QueryTool</a><br/><br/><table width="50%%">
        <tr><td>ID</td><td>TITLE</td><td>PATH</td></tr>
        """ % self.absolute_url()
        
        list = [ (brain.id, brain.Title, brain.getPath()) 
                    for brain in self.executeStringQuery(querystring, **kw) ]
        
        for id,title,path in list:
            ret += "<tr><td>%s</td><td>%s</td><td>%s</td></tr>" % (id, title, path)
        
        ret += '</table>'
        return ret

    security.declareProtected(VM, 'manage_deleteHistory')
    def manage_deleteHistory(self):
        """ Removes all entries from history """

        self.clearQueryHistory()
        return self.REQUEST.RESPONSE.redirect(self.absolute_url() + '/manage_submit_query')

Globals.InitializeClass(QueryTool)
