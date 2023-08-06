from zope.interface import implements
from interfaces import IObjectWithGroup

class ObjectWithGroupMixin(object):
    """
    An implementation of `IObjectWithGroup` ready to be mixed-in another
    class. It works with any class providing the `getId` and `Title` methods.    
    """
    implements(IObjectWithGroup)
    
    group_name_template = 'group_%s'
    """String template for the group name, applied to `self.getId`."""

    group_title_template = 'Members of %s'
    """String template for the group title, applied to `self.Title`."""

    
    def get_group_name(self):
        """Implements: IObjectWithGroup"""
        return self.group_name_template % self.getId()
    
    def get_group_title(self):
        """Implements: IObjectWithGroup"""
        return self.group_title_template % self.Title()
            