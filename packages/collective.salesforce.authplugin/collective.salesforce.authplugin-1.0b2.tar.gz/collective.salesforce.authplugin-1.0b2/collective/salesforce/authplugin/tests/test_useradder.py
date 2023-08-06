from base import SalesforceAuthPluginTestCase
from collective.salesforce.authplugin.config import PROJECTNAME, AUTHMULTIPLUGIN, SF_TEST_OBJECT_TYPE

def add_user_in_test(self, username, password):
    """ Adds a user while recording it in the list of users to automatically remove
        at the end of the tests, to avoid leaving a mess.
    """
    # add user
    self.plugin.doAddUser(username, password)
    
    # query for our new user
    user_list = self.toolbox.query(['UserName__c', 'Id'], SF_TEST_OBJECT_TYPE, "%s = '%s'" % ('UserName__c', username))
    
    # add our user to the _toCleanUp list for removal via the 
    # salesforce api regardless of success/failure
    sfUserId = user_list['records'][0]['Id']
    self._toCleanUp.append(sfUserId)

class TestAuthenticationPlugin(SalesforceAuthPluginTestCase):

    def afterSetUp(self):
        SalesforceAuthPluginTestCase.afterSetUp(self)
        
        # disable the cache for tests in TestAuthenticationPlugin
        self.plugin.ZCacheable_setManagerId(None)
        
        self.acl = self.portal.acl_users
        self.plugins = self.acl.plugins
        self.useradder = getattr(self.acl, AUTHMULTIPLUGIN)
        
        self.username = 'joe'
        self.password = 'password'
        
    def testDoAddUser(self, username = None, password = None):
        if username is not None:
            self.username = username
        if password is not None:
            self.password = password
        
        # make sure no one is there to start
        user_list = self.toolbox.query(['UserName__c'], SF_TEST_OBJECT_TYPE, "%s = '%s'" % ('UserName__c', self.username))
        self.assertEqual(user_list['size'], 0)
        
        # add user
        self.useradder.doAddUser(self.username, self.password)
        
        # query for our new user
        user_list = self.toolbox.query(['UserName__c', 'Id'], SF_TEST_OBJECT_TYPE, "%s = '%s'" % ('UserName__c', self.username))
        
        # add our user to the _toCleanUp list for removal via the 
        # salesforce api regardless of success/failure
        sfUserId = user_list['records'][0]['Id']
        self._toCleanUp.append(sfUserId)
        
        # assert that the new user exists
        self.assertEqual(user_list['size'], 1)
    
    def testDoAddUserAdaptsToSFObjectsWithVaryingFieldRequirements(self):
        # make sure no one is there to start
        user_list = self.toolbox.query(['UserName__c'], "Lead", "%s = '%s'" % ('UserName__c', self.username))
        self.assertEqual(user_list['size'], 0)
        
        # re-configure our useradder
        self.useradder.setSFObjectType('Lead')
        
        # add user
        self.useradder.doAddUser(self.username, self.password)
        
        # query for our new user
        user_list = self.toolbox.query(['UserName__c', 'Id'], "Lead", "%s = '%s'" % ('UserName__c', self.username))
        
        # add our user to the _toCleanUp list for removal via the 
        # salesforce api regardless of success/failure
        sfUserId = user_list['records'][0]['Id']
        self._toCleanUp.append(sfUserId)
        
        # assert that the new user exists
        self.assertEqual(user_list['size'], 1)
        

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestAuthenticationPlugin))
    return suite
