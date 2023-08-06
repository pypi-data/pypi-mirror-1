import logging
import copy
from types import ListType, TupleType

from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from Products.PluggableAuthService.utils import createViewName

logger = logging.getLogger("salesforceauthplugin")

class UserEnumerationMixin:
    """Implement Products.PluggableAuthService.interfaces.plugins.IUserEnumerationPlugin
    """
    security = ClassSecurityInfo()

    #
    #   IUserEnumerationPlugin
    #
    security.declarePrivate('enumerateUsers')
    def enumerateUsers(self, id=None, login=None, exact_match=False,
        sort_by=None, max_results=None, **kw):
        """ See IUserEnumeration
        """
        # # TODO: login vs. id USERNAME_FIELD vs. LOGIN_FIELD

        logger.debug('calling enumerateUsers()...')
        
        view_name = createViewName('enumerateUsers')

        if isinstance(id, str):
            id = [id]
        if isinstance(login, str):
            login = [login]

        # Check cached data
        keywords = copy.deepcopy(kw)
        info = {
            'id': id,
            'login': login,
            'exact_match': exact_match,
            'sort_by': sort_by,
            'max_results': max_results,
        }
        keywords.update(info)
        cached_info = self.ZCacheable_get(view_name=view_name,
                                          keywords=keywords)
        if cached_info is not None:
            return cached_info
            
        terms = []
        if id is not None:
            terms.extend(id)
        if login is not None:
            terms.extend(login)
            
        if len(terms) == 0:
            terms = (None,)
                             
        results = list()        
        for user_id in terms:
            if user_id is None:
                # search all
                query = ""
            else:
                # search specific
                if exact_match:
                    query = "%s='%s'" % (self.getLoginFieldName(), user_id)
                else:
                    query = "%s like '%%%s%%'" % (self.getLoginFieldName(), user_id)
            
            res = self._getSFConnection().query([self.getLoginFieldName()], self._sf_object_type, query)            
            results.extend(self._extractQueryDataForEnum(res))

            # if our query could return more data and we're not
            # up against the limits of our max_results, we'd
            # need to call queryMore
            while not res['done']:
                if max_results and len(results) >= max_results:
                    break
                res = self._getSFConnection().queryMore(res['queryLocator'])
                results.extend(self._extractQueryDataForEnum(res))
            
            if max_results and len(results) >= max_results:
                 break
            
        if max_results:
            results = results[:max_results]
        if sort_by:
            results.sort(key=lambda a: a[sort_by])
            
        retvals = tuple(results)

        # Cache data upon success
        self.ZCacheable_set(retvals, view_name=view_name, keywords=keywords)
        
        return retvals
    
    #
    # IUserEnumerationPlugin helper methods
    # 
    security.declarePrivate('_extractQueryDataForEnum')
    def _extractQueryDataForEnum(self, res):
        """Accepts a Salesforce.com query result
           set and extracts id, login, and sets pluginid
           for the IUserEnumerationPlugin
        """
        results = list()
        for r in res['records']:
            username = r[self.getLoginFieldName()]
            data = dict(id=username, login=username, 
                pluginid=self.getId())
            results.append(data)
        return results
    

InitializeClass(UserEnumerationMixin)