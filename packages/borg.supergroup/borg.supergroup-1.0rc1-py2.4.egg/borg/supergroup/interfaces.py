from zope.interface import Interface

class ISuperGroups(Interface):
    """The plugin will look up subscription adapters on the current user that
    provide this interface.
    """
    
    def __call__():
        """Return an iterable of the group ids for the adapted principal
        """
        
class ISuperGroupsEnumeration(Interface):
    """The plugin will look up all registered utilities for this interface
    """
        
    def enumerate_groups(id=None, exact_match=False, **kw):
        """Return an iterable of group info that match the given id exactly 
        (if exact_match is given), or partially (if not). Group info is a dict
        with keys id, title.
        """