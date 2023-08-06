
from persistent.cPersistence import Persistent
import md5
import re
import Globals

from Products.AdvancedQuery.AdvancedQuery import Eq, In, Le, Ge, \
     MatchGlob, MatchRegexp, \
     Between, Not, And, Or, Generic, Indexed
               
from Products.AdvancedQuery.AdvancedQuery import _QueryContext

from SearchOperators import Count, Sum, Avg, Around, IIntResult
from SearchOperators import Linked as _Linked

from AccessControl import ClassSecurityInfo

import logging
log = logging.getLogger('QueryTool')

class Query(Persistent):
    """
    Class that encapsulates a query.
    """


    security = ClassSecurityInfo()

    def __init__(self, name, *args, **kw):
        self._query = None
        self.setName(name)
        self.setCachingEnabled(False)
        self.clearCache()
        
        self._catalogname = kw.get('catalog', 'portal_catalog')
        self._wrap_security = True

    security.declarePublic('getName')
    def getName(self):
        """ Returns the name of the query """

        return self._name

    def setName(self, name):
        """ Sets the name for the query """

        self._name = name

    security.declarePublic('getWrapSecurity')
    def getWrapSecurity(self):
        """ If this is set to false then no additional checks are 
        done in catalog search (like allowedRolesAndUsers or expires) """

        if hasattr(self, '_wrap_security'):
            return self._wrap_security

        return True

    def setWrapSecurity(self, value):
        self._wrap_security = value

    security.declarePublic('getCatalog')
    def getCatalog(self):
        """ Gets the name for the catalog used for this query """

        if hasattr(self, '_catalogname'):
            if self._catalogname:
                return self._catalogname

        return 'portal_catalog'

    def setCatalog(self, name):
        self._catalogname = name

    def createFromString(self, querystring, replacespecial=True):
        """ Initialize from given string """

        self._origquery = querystring
        if replacespecial is True:
            self._query = querystring.replace('\n', ' ').replace('\r', ' ').strip()
        else: self._query = querystring.strip()

        self.clearCache()
        return self
   
    def setCachingEnabled(self, enable=True):
        """ Activates caching """

        self._caching_enabled = enable
        if not enable:
            self.clearCache()
   
    def canCache(self):
        """ Returns true if we can cache """

        return self._caching_enabled
   
    def clearCache(self):
        """ Clears the result cache """
    
        self._cache = None
        self._cached_params = {}
        self._cached_md5 = None

    def hasCachedResult(self):
        """ Returns True if there is a cached result """

        if not self.canCache(): return False 
        return (self._cache != None)

    security.declarePublic('getCachedResult')
    def getCachedResult(self, **kw):
        """ Returns the cached resultset. If there is
        no such one then returns None """

        if not self.canCache():
            return None

        # We can only return cached result
        # if parameters are the same
        md = md5.md5(str(kw)).hexdigest()
        if md == self._cached_md5:
            return self._cache

        return None

    security.declarePublic('saveCachedResult')
    def saveCachedResult(self, result, **kw):
        """ Saves the result """

        if not self.canCache():
            return
        
        # Only save if the new one has changed
        if self.getCachedResult(**kw):
            return

        self._cache = result
        self._cached_params = kw

        # save md5 for further check
        self._cached_md5 = md5.md5(str(kw)).hexdigest()

    security.declarePublic('execute')
    def execute(self, context, catalog, **kw):
        """ Execute saved query. If cache parameter is set
        to True, then there is a check for cached versions of
        the result """ 

        filtering = ()
        if kw.has_key('sort_on_filter'):
            filtering = kw.get('sort_on_filter')
            del kw['sort_on_filter']

        # Look if we have a valid link manager out there
        if self._query.find('Linked') >= 0:
            lob = context.getLinkManagerObject()
            if not lob:
                raise Exception, 'Could not find link manager! Please set properties of QueryTool!'

            # prepare function for link checking
            Linked = lambda source, type, target, direction='target': _Linked(source, type, target, direction, lob)

        # Do we have a cache set?
        if self.canCache():
            if self.getCachedResult(**kw):
                return self.getCachedResult(**kw)

        # get instances of the specified query types using specified params
        cleaned = self._insertParams(**kw)
        log.debug('Executing Query on %s: %s' % (catalog.getId(), cleaned))

        # because queries can have a TODAY flag set we need to set it here
        if cleaned.find('TODAY')>0:
            TODAY = catalog.ZopeTime()

        iquery = eval(cleaned)

        # go ahead and eval query with specified catalog
        if IIntResult.isImplementedBy(iquery):
            result = iquery._eval(_QueryContext(catalog))
        else:
            result = catalog.evalAdvancedQuery(iquery, sortSpecs=filtering, wrapSecurity=self.getWrapSecurity())

        # Save the result
        if self.canCache():
            self.saveCachedResult(result, **kw)
        return result

    def _insertParams(self, **kw):
        """ Inserts parameters given into query and returns query """

        if not self._query.find('$') >= 0:
            return self._query

        # first clean up query
        thequery = self._query.replace('\n', '').replace('\r', '').strip()

        # first search for conditionals - we allow if and ifnot
        found = thequery.find('[[if')
        if found >= 0:
            # [[if|ifnot(<fieldname>)]]<expression>[[endif]]
            # fieldname can be PARAMETERS_GIVEN which is a constant
            # that evaluate to true if there are parameters at all
            pattern = re.compile(r"""
                    \[\[
                    (if|ifnot)\(    # we allow if and ifnot
                    (.*?)           # the name of the field
                    \)]]
                    (.*?)           # the expression
                    \[\[endif\]\]
                    """, re.VERBOSE | re.MULTILINE | re.IGNORECASE)

            endpoint = 0; EMPTY_REPLACE = r''
            while endpoint < len(thequery):
                sres = pattern.search(thequery, endpoint)
                if sres != None:
                    command, fieldname, expression = sres.groups()
                    expression = expression.strip()

                    if fieldname == 'PARAMETERS_GIVEN':
                        if command == 'if' and len(kw)>0:
                            thequery = pattern.sub(r'\3', thequery, 1)

                        elif command == 'if' and not len(kw)>0:
                            thequery = pattern.sub(EMPTY_REPLACE, thequery, 1)
                        
                        elif command == 'ifnot' and len(kw)==0:
                            thequery = pattern.sub(r'\3', thequery, 1)

                        elif command == 'ifnot' and not len(kw)==0:
                            thequery = pattern.sub(EMPTY_REPLACE, thequery, 1)

                    elif command == 'if' and fieldname.replace('$', '') in kw.keys():
                        # conditional fulfilled - taking expression in
                        thequery = pattern.sub(r'\3', thequery, 1)

                    elif command == 'if' and fieldname.replace('$', '') not in kw.keys():
                        thequery = pattern.sub(EMPTY_REPLACE, thequery, 1)

                    elif command == 'ifnot' and not fieldname.replace('$', '') in kw.keys():
                        # conditional not - fulfilled
                        thequery = pattern.sub(r'\3', thequery, 1)

                    elif command == 'ifnot' and fieldname.replace('$', '') in kw.keys():
                        thequery = pattern.sub(EMPTY_REPLACE, thequery, 1)

                    endpoint = sres.start()+1 # we can not use end here because we replace string
                else:
                    break

        qs = thequery
        for key in kw.keys():
            if qs.find('$%s' % key) >= 0:
                qs = qs.replace('$%s' % key, str(kw[key]))

        if qs.find('$') >= 0:
            raise Exception, 'Not all parameters given for %s (kw: %s)' % (qs, str(kw))

        return qs

    def __str__(self):
        """ Returns string repr of query """

        return self._query

    security.declarePublic('getRawQueryString')
    def getRawQueryString(self):
        if hasattr(self, '_origquery'):
            return self._origquery
        return self._query

Globals.InitializeClass(Query)
