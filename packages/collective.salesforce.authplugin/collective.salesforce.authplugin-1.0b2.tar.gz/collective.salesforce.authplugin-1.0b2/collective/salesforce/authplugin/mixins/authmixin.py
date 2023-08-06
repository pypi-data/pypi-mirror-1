import sha
import logging
import warnings
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo

from Products.PluggableAuthService.utils import createViewName

from collective.salesforce.authplugin import config
from collective.salesforce.authplugin import encrypt

logger = logging.getLogger("salesforceauthplugin")

_marker = []

class AuthMixin:
    """Implements 
       Products.PluggableAuthService.interfaces.plugins.IAuthenticationPlugin
    """
    security = ClassSecurityInfo()
    
    default_encryption = encrypt.DEFAULT_ENCRYPTION
    
    #
    #  IAuthenticationPlugin
    #
    security.declarePrivate('authenticateCredentials')
    def authenticateCredentials(self, credentials):
        """ See IAuthenticationPlugin
        """
        login = credentials.get('login')
        logger.debug('Calling authenticateCredentials for %s' % login)

        # make sure plugin was correctly configured
        if not self.getLoginFieldName() or not self.getPasswordFieldName():
            warnings.warn("""Configuration Error: You've configured your SalesforceAuthPlugin as an"""
                          """ IAuthenticationPlugin, but you have not chosen which Salesforce fields"""
                          """ to use for username and password.""",
                          UserWarning,
                          stacklevel=1)
            
            return None
        
        password = credentials.get('password')
        view_name = createViewName('authenticateCredentials', login)
        if config.CACHE_PASSWORDS:
            cached_info = self.ZCacheable_get(view_name=view_name,
                    keywords={'password':sha.sha(password).hexdigest()},
                    default=_marker)
            if cached_info is not _marker:
                return cached_info
        
        retval = None
        fields, objectType, conditionStatement = self._buildAuthenticationQuery(credentials)
        res = self._getSFConnection().query(fields, objectType, str(conditionStatement))
        if res['size'] == 1:
            username = res['records'][0][self.getLoginFieldName()]
            encrypted_password = res['records'][0][self.getPasswordFieldName()]
            
            encrypter = encrypt.find_encrypter(self.default_encryption)
            if encrypter is None:
                raise LookupError('Could not find an encrypter for "%s"'
                                  % self.default_encryption)

            if encrypter.validate(encrypted_password, password):
                retval = (username, username)
        # If more than one user is returned, we can't authenticate anyone, but we still 
        # want to cache this result so we don't call Salesforce every time
        else:
            logger.debug("Found %s users for id: [%s]. Can't return user info..." % (res['size'], login))
            retval = None
            
        if config.CACHE_PASSWORDS:
            self.ZCacheable_set(retval, view_name=view_name, keywords={'password':sha.sha(password).hexdigest()})
        
        return retval
    
    #
    # IAuthenticationPlugin helper methods
    # 
    security.declarePrivate('_buildAuthenticationQuery')
    def _buildAuthenticationQuery(self, credentials):
        login = credentials.get('login')
        password = credentials.get('password')        
        conditionString = "%(usernameField)s='%(username)s'" % \
                                {'usernameField':self.getLoginFieldName(),
                                 'username':login}
        if self.getAuthConditionClause():
            addlConditionString = self.getAuthConditionClause()
            conditionString += ' and ' + addlConditionString
        return [self.getLoginFieldName(), self.getPasswordFieldName()], self._sf_object_type,  conditionString

    
InitializeClass(AuthMixin)
