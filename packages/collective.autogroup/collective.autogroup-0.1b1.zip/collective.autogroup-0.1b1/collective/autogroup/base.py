from Products.PlonePAS.plugins.autogroup import AutoGroup
from Products.CMFCore.utils import getToolByName

class MembershipCriteriaAutoGroup(AutoGroup):
    """
    Specialization of `AutoGroup` which uses an `IMembershipCriteria` callable
    to define the group members.
    """
    
    def __init__(self, id, criteria, group_name=None, title=''):
        """
        Arguments:
        id -- Plugin id.
        criteria -- A callable implementing `IMembershipCriteria`.
        group_name -- The name of the group to be created, a.k.a ID.
        title -- The title of the group to be created.
        """        
        AutoGroup.__init__(
            self, 
            id=id, 
            title=title, 
            group=group_name, 
            description=title, # Workaround AutoGroup bug.
        )   
        self.criteria = criteria     
    
    def getGroupsForPrincipal(self, principal, request=None):
        return (self.criteria(principal) and (self.group,)) or tuple()
    
    def getGroupMembers(self, group_id):
        if group_id != self.group:
            return tuple()
                
        mtool = getToolByName(self, 'portal_membership')
        return [m.getId() for m in mtool.listMembers() if self.criteria(m)]
         
