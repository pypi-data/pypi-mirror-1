#coding=utf8
from interfaces import IGroupManager

def get_groups_tool():
    return getToolByName(getSite(), 'portal_groups')

def initialized(obj, event):
    group_name = obj.get_group_name()    
    group_manager = IGroupManager(obj)
    group_manager.create_group(group_name)
    group_manager.set_group_title(group_name, obj.get_group_title())
    
def edited(obj, event):
    group_manager = IGroupManager(obj)
    group_manager.set_group_title(obj.get_group_name(), obj.get_group_title())
    
def removed(obj, event):
    group_manager = IGroupManager(obj)
    group_name = obj.get_group_name()
    
    if group_manager.group_exists(group_name):
        group_manager.remove_group(group_name)
        
