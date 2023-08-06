from base import SalesforceAuthPluginTestCase
from collective.salesforce.authplugin.config import PROJECTNAME, AUTHMULTIPLUGIN, SF_TEST_OBJECT_TYPE

class TestUserEnumerationPlugin(SalesforceAuthPluginTestCase):

    def afterSetUp(self):
        SalesforceAuthPluginTestCase.afterSetUp(self)
        
        # disable the cache for tests in TestAuthenticationPlugin
        self.plugin.ZCacheable_setManagerId(None)
        
        self.acl = self.portal.acl_users
        self.plugins = self.acl.plugins
        self.userenumerator = getattr(self.acl, AUTHMULTIPLUGIN)
        self.username = 'plonetestcase'
        self.password = 'password'
    
    def testEnumerateUsers(self):
        # any given salesforce instance may start with
        # objects that fullfill the basic enumerateUsers 
        # criteria.  This becomes our offset for calls 
        # to enumerateUsers w/ no id or login
        return_offset = len(self.userenumerator.enumerateUsers())
        
        count = 10 
        
        for x in range(count):
            username = '%s_user_%i' % (self.username, x)
            obj = dict(type=SF_TEST_OBJECT_TYPE,
                LastName=username,
                UserName__c=username,
                Password__c=self.password,
            )
            
            res = self.toolbox.create(obj)
            # add our user to the _toCleanUp list for removal via the 
            # salesforce api regardless of success/failure
            sfUserId = res[0]['id']
            self._toCleanUp.append(sfUserId)
            
        
        ret = self.userenumerator.enumerateUsers()
        self.assertEqual(len(ret), count + return_offset)
        
        ret = self.userenumerator.enumerateUsers(id='%s_user_1' % self.username, exact_match=True)
        self.assertEqual(len(ret), 1)              
        
        # make sure required keys are returned
        for k in ('id', 'login', 'pluginid'):
            self.failUnless(k in ret[0].keys())
        
        ret = self.userenumerator.enumerateUsers(login='%s_user_1' % self.username, exact_match=True)
        self.assertEqual(len(ret), 1)
        
        # searching multiple ids
        ret = self.userenumerator.enumerateUsers(id=('%s_user_1' % self.username, '%s_user_2' % self.username), exact_match=True )
        self.assertEqual(len(ret), 2)

        # searching multiple logins, sorted by id
        ret = self.userenumerator.enumerateUsers(login=('%s_user_2' % self.username, '%s_user_1' % self.username), exact_match=True, sort_by='id' )
        self.assertEqual(len(ret), 2)
        self.failUnless(ret[0]['id'].endswith('1'))
        self.failUnless(ret[1]['id'].endswith('2'))
        
        # non-exact search
        ret = self.userenumerator.enumerateUsers(id='user_1', exact_match=False)
        self.assertEqual(len(ret), 1)
        
        # can limit using max_results
        ret = self.userenumerator.enumerateUsers(max_results=5)
        self.assertEqual(len(ret), 5)
        
        ret = self.userenumerator.enumerateUsers(max_results=20)
        if return_offset + len(ret) <= 20:
            self.assertEqual(len(ret), count + return_offset)
        else:
            self.assertEqual(len(ret), 20)
    

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestUserEnumerationPlugin))
    return suite
