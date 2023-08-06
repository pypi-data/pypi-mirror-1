from interfaces import IGroupManager
from zope.interface import implements
from zope.app.component.hooks import getSite
from Products.CMFCore.utils import getToolByName

class PortalGroupsGroupManager(object):
    """Implementation of `IGroupManager` which uses the `portal_groups` tool."""    
    implements(IGroupManager)
    
    def __init__(self, obj=None):
        self.obj = obj
        self.portal = getSite()
        self.portal_groups_tool = getToolByName(self.portal, 'portal_groups')
        
    def _get_group(self, name):
        return self.portal_groups_tool.getGroupById(name)
    
    def create_group(self, name):
        self.portal_groups_tool.addGroup(id=name)
        
    def remove_group(self, name):
        self.portal_groups_tool.removeGroups([name])
    
    def group_exists(self, name):
        return self._get_group(name) is not None
        
    def set_group_title(self, name, title):
        self.portal_groups_tool.editGroup(id=name, title=title)
        
    def get_group_title(self, name):
        return self._get_group(name).getProperty('title')
    
