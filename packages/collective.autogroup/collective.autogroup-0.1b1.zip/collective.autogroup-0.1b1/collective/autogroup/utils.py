from base import MembershipCriteriaAutoGroup
from Products.PlonePAS.Extensions.Install import activatePluginInterfaces
from Acquisition import aq_parent, aq_inner
from StringIO import StringIO

def get_plugin_id(group_name):
    return '%s_auto_group_plugin' % group_name
    
def get_plugin(acl_users, group_name):
    plugin_id = get_plugin_id(group_name)
    return getattr(acl_users, plugin_id)

def create_auto_group(
    acl_users, 
    criteria, 
    group_name, 
    title=''):
    """
    Create an automatic group.
    
    Arguments:
    acl_users -- An `acl_users` folder which resides in the portal root.
    criteria -- A callable implementing `IMembershipCriteria`.
    group_name -- The name of the group to be created, a.k.a ID.
    title -- The title of the group to be created.
    """
    plugin_id = get_plugin_id(group_name)
    plugin = MembershipCriteriaAutoGroup(
        id=plugin_id,
        criteria=criteria, 
        group_name=group_name,
        title=title,
    )
    acl_users._setObject(plugin_id, plugin)
    portal = aq_parent(aq_inner(acl_users))
    activatePluginInterfaces(portal, plugin_id, StringIO())
    
def remove_auto_group(acl_users, group_name):
    acl_users.manage_delObjects(ids=[get_plugin_id(group_name)])
    
def set_auto_group_title(acl_users, group_name, title):
    get_plugin(acl_users, group_name).description = title
    
def get_auto_group_title(acl_users, group_name):
    return get_plugin(acl_users, group_name).description
