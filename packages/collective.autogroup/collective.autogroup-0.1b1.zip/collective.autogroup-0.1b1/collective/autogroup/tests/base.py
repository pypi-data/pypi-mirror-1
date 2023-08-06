"""Setup the environment for tests."""
from Products.PloneTestCase import PloneTestCase as ptc
from Products.CMFCore.utils import getToolByName
from Products.PloneTestCase.setup import default_password


class BaseTestCase(ptc.PloneTestCase):
    
    def afterSetUp(self):
        self.membership = getToolByName(self.portal, 'portal_membership')
        self.acl_users = getToolByName(self.portal, 'acl_users')
            
    def add_user(self, userid, roles=['Member'], password=default_password):
        """Add an user to the portal."""
        self.membership.addMember(userid, password, roles, []) 
        return self.membership.getMemberById(userid)
  
ptc.setupPloneSite()
