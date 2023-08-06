from zope.interface import Interface

class IMembershipCriteria(Interface):
    """
    Defines a criteria to decide whether an user belongs or not to a group.
    """
    
    def __call__(principal):
        """
        Arguments:
        principal -- A PAS user or group object. More formally: an instance
            of `AccessControl.User.BasicUser`.
            
        Return: a boolean which is True if and only if `principal` is a member
            of the group.
        """
    
