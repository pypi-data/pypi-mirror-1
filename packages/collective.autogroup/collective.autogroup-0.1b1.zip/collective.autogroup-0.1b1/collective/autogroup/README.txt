collective.autogroup
====================

Overview
--------

This package provide a simple API to create automatic groups in Plone. Automatic
groups are users groups that have its member set automaticaly calculated. The
``AuthenticatedMembers`` group is an example automatic group, created by Plone.

Creating an automatic group is simple:

1. Create a class implementing ``IMembershipCriteria``. This class define a 
   criteria to decied whether an user belongs or not to the group.
   
2. Call ``utils.create_auto_group`` passing an instance of 
   ``IMembershipCriteria`` and other info about the group. 
   
Inside the ``utils`` module there are other useful functions.

Example usage
-------------

Use case: we want to create an automatic group containing all users whose ID 
begins with an 'r' letter.

First we create a class implementing ``IMembershipCriteria``::
    
    >>> from collective.autogroup.interfaces import IMembershipCriteria
    >>> from zope.interface import implements
    >>> class MembershipCriteria(object):
    ...     implements(IMembershipCriteria)
    ...     def __call__(self, principal):
    ...         return principal.getId()[0] == 'r'
    
Now we create the auto group using this criteria::

    >>> from Products.CMFCore.utils import getToolByName
    >>> from collective.autogroup.utils import create_auto_group
    >>> group_name = 'r_users'
    >>> group_title = 'Members of r_users'
    >>> create_auto_group(
    ...     acl_users=self.portal.acl_users, 
    ...     criteria=MembershipCriteria(), 
    ...     group_name=group_name, 
    ...     title=group_title,
    ... )    
    >>> gtool = getToolByName(self.portal, 'portal_groups')
    >>> group = gtool.getGroupById(group_name)
    >>> group is not None
    True
    
The group should be empty for now, since we don't have any users matching the
criteria::
        
    >>> len(group.getAllGroupMemberIds())
    0
    
Create some users and see what happens::

    >>> user1 = self.add_user('ronaldo')
    >>> user2 = self.add_user('romario')         
    >>> user3 = self.add_user('tostao')
    >>> sorted(group.getGroupMemberIds())
    ['romario', 'ronaldo']
    >>> group_name in user1.getGroups()
    True
    >>> group_name in user2.getGroups()
    True
    >>> group_name in user3.getGroups()
    False
    
About the group title
---------------------

Check this out::

    >>> not group.getProperty('title')
    True
    
It seems the title of the group is empty, even though we set the title to 
``group_title`` when we called ``create_auto_group``. It turns out
``prefs_groups_overview`` and other Plone templates do not call
``group.getProperty`` to get the group title. Even the ``AuthenticatedUsers``
group (created by Plone) does not have the title property set::

    >>> not gtool.getGroupById('AuthenticatedUsers').getProperty('title')
    True

The ``prefs_groups_overview`` template uses the following method to get the
group title::
    
    >>> search_results = self.portal.acl_users.searchGroups(id=group_name)
    >>> search_results[0]['title'] == group_title
    True   
    
To change the title of an automatic group we should not call 
``group.setProperty``, it will not work. The correct way is change the 
``description`` property of the correspondent PAS plugin (yes, it's the 
``description`` property, not ``title``). Fortunately this package provides
a function that makes this job easier::

    >>> from collective.autogroup.utils import (set_auto_group_title, 
    ...     get_auto_group_title)
    >>> new_title = group_title + '_new'
    >>> set_auto_group_title(self.acl_users, group_name, new_title)
    >>> search_results = self.portal.acl_users.searchGroups(id=group_name)
    >>> search_results[0]['title'] == new_title
    True
    >>> get_auto_group_title(self.acl_users, group_name) == new_title
    True

It can also be done through ZMI.

Credits
-------

- Rafael Oliveira <rafaelbco@gmail.com>: Author.
