from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

from zope.component import subscribers, getAllUtilitiesRegisteredFor

from Products.PluggableAuthService.utils import classImplements
from Products.PluggableAuthService.plugins.BasePlugin import BasePlugin

from Products.PluggableAuthService.interfaces.plugins import IGroupEnumerationPlugin
from Products.PluggableAuthService.interfaces.plugins import IGroupsPlugin

from borg.supergroup.interfaces import ISuperGroups
from borg.supergroup.interfaces import ISuperGroupsEnumeration

manage_addSuperGroupProviderForm = PageTemplateFile(
        "zmi/addSuperGroupProviderForm.pt", globals(),
        __name__="manage_addSuperGroupProviderForm")

def manage_addSuperGroupProvider(dispatcher, id, title=None, REQUEST=None):
    """Add a SuperGroupProvider to a Pluggable Authentication Services."""
    plugin = SuperGroupProvider(id, title)
    dispatcher._setObject(plugin.getId(), plugin)

    if REQUEST is not None:
        REQUEST.RESPONSE.redirect(
                '%s/manage_workspace?manage_tabs_message=Super+group+provider+added.'
                % dispatcher.absolute_url())

class SuperGroupProvider(BasePlugin):
    """This is the actual plug-in. It takes care of looking up
    ISuperGroups subscription adapters (when available) and 
    ISuperGroupsEnumeration utilities (when available), and providing groups
    accordingly.
    
    Let us first test that we can look up additional groups. For testing, we
    will create an instance of the plugin explicitly.
    
        >>> from borg.supergroup.plugin import SuperGroupProvider
        >>> plugin = SuperGroupProvider('borg.supergroup')
        
    We need a dummy user type to test on:
    
        >>> class DummyUser(object):
        ...     def __init__(self, uid, group_ids=()):
        ...         self.id = uid
        ...         self._groups = group_ids
        ...     
        ...     def getId(self):
        ...         return self.id
        ...     
        ...     def _check_context(self, obj):
        ...         return True
        ...     
        ...     def getGroups(self):
        ...         return self._groups
        ...     
        ...     def getRoles(self):
        ...         return ()

    Then we will register two subscription adapters.
    
        >>> from zope import component
        >>> from zope import interface
        
        >>> from borg.supergroup.interfaces import ISuperGroups
        
        >>> class AlphaGroup(object):
        ...     interface.implements(ISuperGroups)
        ...     component.adapts(DummyUser)
        ...
        ...     def __init__(self, context):
        ...         self.context = context
        ...
        ...     def __call__(self):
        ...         return ['Alpha']
    
        >>> class BetaGroup(object):
        ...     interface.implements(ISuperGroups)
        ...     component.adapts(DummyUser)
        ...
        ...     def __init__(self, context):
        ...         self.context = context
        ...
        ...     def __call__(self):
        ...         if self.context.getId().startswith('beta'):
        ...             return ['Beta', 'Gamma']
        ...         else:
        ...             return ['Gamma']
        
        >>> component.provideSubscriptionAdapter(AlphaGroup)
        >>> component.provideSubscriptionAdapter(BetaGroup)
        
    We should now be able to get this information back from the plugin.
    
        >>> alpha_user = DummyUser('alpha')
        >>> beta_user = DummyUser('beta')
        
        >>> sorted(plugin.getGroupsForPrincipal(alpha_user))
        ['Alpha', 'Gamma']
        
        >>> sorted(plugin.getGroupsForPrincipal(beta_user))
        ['Alpha', 'Beta', 'Gamma']

    Now we can test enumeration. This essentially helps power interfaces that
    search for groups irrespective of a user.
    
        >>> from borg.supergroup.interfaces import ISuperGroupsEnumeration
    
        >>> class AlphaGroupEnumeration(object):
        ...     interface.implements(ISuperGroupsEnumeration)
        ...
        ...     def enumerate_groups(self, id=None, exact_match=False, **kw):
        ...         if not id:
        ...             return [{'id': 'Alpha', 'title': 'Alpha Group'}]
        ...         if (exact_match and id == 'Alpha') or (not exact_match and id in 'Alpha'):
        ...             return [{'id': 'Alpha', 'title': 'Alpha Group'}]
        ...         return []
        
        >>> class BetaGroupEnumeration(object):
        ...     interface.implements(ISuperGroupsEnumeration)
        ...
        ...     def enumerate_groups(self, id=None, exact_match=False, **kw):
        ...         if not id:
        ...             return [{'id': 'Beta', 'title': 'Beta Group'}, 
        ...                     {'id': 'Gamma', 'title': 'Gamma Group'}]
        ...
        ...         found = []
        ...         if (exact_match and id == 'Beta') or (not exact_match and id in 'Beta'):
        ...             found.append({'id': 'Beta', 'title': 'Beta Group'})
        ...         if (exact_match and id == 'Gamma') or (not exact_match and id in 'Gamma'):
        ...             found.append({'id': 'Gamma', 'title': 'Gamma Group'})
        ...         return found
        
        >>> alpha_groups = AlphaGroupEnumeration()
        >>> beta_groups = BetaGroupEnumeration()
        >>> component.provideUtility(alpha_groups, name='alpha')
        >>> component.provideUtility(beta_groups, name='beta')
        
    Notice how the plugin provides some additional information for each item:
        
        >>> plugin.enumerateGroups(id='Alpha', exact_match=True)
        [{'pluginid': 'borg.supergroup', 'id': 'Alpha', 'title': 'Alpha Group'}]
        
        >>> plugin.enumerateGroups(id='Al', exact_match=False)
        [{'pluginid': 'borg.supergroup', 'id': 'Alpha', 'title': 'Alpha Group'}]
        
        >>> plugin.enumerateGroups(id='Gamma', exact_match=False)
        [{'pluginid': 'borg.supergroup', 'id': 'Gamma', 'title': 'Gamma Group'}]
        
        >>> plugin.enumerateGroups() # doctest: +NORMALIZE_WHITESPACE
        [{'pluginid': 'borg.supergroup', 'id': 'Alpha', 'title': 'Alpha Group'}, 
         {'pluginid': 'borg.supergroup', 'id': 'Beta', 'title': 'Beta Group'}, 
         {'pluginid': 'borg.supergroup', 'id': 'Gamma', 'title': 'Gamma Group'}]
        
        >>> plugin.enumerateGroups(sort_by='title') # doctest: +NORMALIZE_WHITESPACE
        [{'pluginid': 'borg.supergroup', 'id': 'Alpha', 'title': 'Alpha Group'}, 
         {'pluginid': 'borg.supergroup', 'id': 'Beta', 'title': 'Beta Group'}, 
         {'pluginid': 'borg.supergroup', 'id': 'Gamma', 'title': 'Gamma Group'}]
        
        >>> plugin.enumerateGroups(sort_by='title', max_results=1)
        [{'pluginid': 'borg.supergroup', 'id': 'Alpha', 'title': 'Alpha Group'}]
        
    """

    meta_type = "Super Group Provider"
    security  = ClassSecurityInfo()

    def __init__(self, id, title=""):
        self.id = id
        self.title = title

    #
    # IGroupsPlugin implementation
    #

    security.declarePrivate("getGroupsForPrincipal")
    def getGroupsForPrincipal(self, principal, request=None):
        for provider in subscribers((principal,), ISuperGroups):
            for group in provider():
                yield group

    # 
    # IGroupEnumerationPlugin implementation
    # 

    security.declarePrivate("enumerateGroups")
    def enumerateGroups(self, id=None, exact_match=False, sort_by=None, 
                        max_results=None, **kw):
        pluginid = self.getId()
        groups = []
        
        for enumerator in getAllUtilitiesRegisteredFor(ISuperGroupsEnumeration):
            for group in enumerator.enumerate_groups(id, exact_match, **kw):
                scribbled = group.copy()
                scribbled['pluginid']=pluginid
                groups.append(scribbled)
        
        if sort_by:
            def sort_cmp(left, right):
                if sort_by in left and sort_by in right:
                    return cmp(left[sort_by], right[sort_by])
                else:
                    return 0
            groups.sort(cmp=sort_cmp)
            
        if max_results:
            return groups[:max_results]
        else:
            return groups

classImplements(SuperGroupProvider, IGroupEnumerationPlugin, IGroupsPlugin)
InitializeClass(SuperGroupProvider)
