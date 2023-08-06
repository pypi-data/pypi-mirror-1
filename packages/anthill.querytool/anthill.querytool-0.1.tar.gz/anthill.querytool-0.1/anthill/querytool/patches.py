from Products.CMFCore.utils import getToolByName

from Products.AdvancedQuery import Eq, In, Le, Ge, \
     MatchGlob, MatchRegexp, \
     Between, Not, And, Or, Generic, Indexed, \
     _CompositeQuery, LiteralResultSet

from Products.AdvancedQuery.eval import eval as _eval
from Products.AdvancedQuery.ranking import RankByQueries_Sum, RankByQueries_Max

try: 
    from Products.CMFCore.CatalogTool import CatalogTool
except ImportError: 
    CatalogTool = None

from config import IMPLICIT_LANGUAGE_FILTER

import logging
log = logging.getLogger('anthill.querytool')

if CatalogTool:
  
  # need to check if patch already there
  if not hasattr(CatalogTool, 'evalAdvancedQuery'):
    raise Exception, 'You must have AdvancedQuery installed *and* it must be loaded before this package!'

  from Products.CMFCore.CatalogTool import _getAuthenticatedUser, _checkPermission, AccessInactivePortalContent

  def _evalAdvancedQuery(self,query,sortSpecs=(),wrapSecurity=True):
    '''evaluate *query* for 'CatalogTool' and sort results according to *sortSpec*.'''
    query = query._clone()

    # Make it possible to ignore security assertions
    if wrapSecurity is True:
        # taken from 'CatalogTool.searchResults'
        user = _getAuthenticatedUser(self)
        query &= In('allowedRolesAndUsers',self._listAllowedRolesAndUsers(user))
        if not _checkPermission(AccessInactivePortalContent,self):
          now= self.ZopeTime()
          if 'ValidityRange' in self.Indexes.objectIds():
            query &= Eq('ValidityRange', now)
          else:
            if 'effective' in indexes: query &= Le('effective', now)
            if 'expires' in indexes: query &= Ge('expires', now)

    # lets filter by language
    if getToolByName(self, 'portal_quickinstaller') and IMPLICIT_LANGUAGE_FILTER is True:
        if getToolByName(self, 'portal_quickinstaller').isProductInstalled('LinguaPlone'):
            query &= Eq('Language', getToolByName(self, 'portal_languages').getPreferredLanguage())

    return _eval(self,query,sortSpecs)

  CatalogTool.evalAdvancedQuery= _evalAdvancedQuery
  log.info('Patched AdvancedQuery to allow security assertions')
del CatalogTool
