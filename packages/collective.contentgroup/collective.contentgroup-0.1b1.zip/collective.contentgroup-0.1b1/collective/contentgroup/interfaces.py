from zope.interface import Interface

class IObjectWithGroup(Interface):
    """
    Objects implementing this interface will have a new group created and 
    associated to the object.    
    """
    
    def get_group_name():
        """
        Return the name (ID) of the group associated with the object. 
        This must not change after the object is initialized.
        """
    
    def get_group_title():
        """
        Return the title of the group associated with the object.        
        The group title will be updated whenever the object is edited, i.e
        the `Products.Archetypes.interfaces.IObjectEditedEvent` is fired.
        """
     
class IGroupManager(Interface):
    """Manage groups."""
    
    def create_group(name):
        """Create a group with the given `name`."""
        
    def remove_group(name):
        """Create the group with the given `name`."""    

    def group_exists(name):
        """
        Return a boolean which is True if and only if the group with the 
        given `name` exists.
        """

    def get_group_title(name):
        """Get the title for the group with the given `name`."""
            
    def set_group_title(name, title):
        """Set the title for the group named by `name` to `title`."""
        
    
        
