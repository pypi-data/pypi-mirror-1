from Acquisition import aq_inner
from AccessControl import Unauthorized
from zExceptions import Forbidden
from zope.component import getUtilitiesFor, queryUtility, getMultiAdapter

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName

from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import PloneMessageFactory as _
from Products.statusmessages.interfaces import IStatusMessage

from plone.app.workflow.browser.sharing import SharingView as BaseSharingView
from plone.memoize.instance import memoize

class SharingView(BaseSharingView):
    """Sharing view specific to content"""
    template = ViewPageTemplateFile('templates/sharing.pt')
    
    @memoize
    def search_results(self):
        user_results = self.user_search_results()
        group_results = self.group_search_results()
        
        return group_results + user_results
    
    def createGroup(self, group_name, group_users=[]):
        context = aq_inner(self.context)
        acl_users = getToolByName(context, 'acl_users')
        portal_groups = getToolByName(context, 'portal_groups')
        plone_utils = getToolByName(context, 'plone_utils')
        
        success = portal_groups.addGroup(group_name)
        if not success:
            return False
        else:
            group = portal_groups.getGroupById(group_name)
            for u in group_users:
                group.addMember(u)
            return True
    
    @memoize
    def role_settings(self):
        """Get current settings for users and groups for which settings have been made.
        
        Returns a list of dicts with keys:
        
         - id
         - title
         - type (one of 'group' or 'user')
         - roles
         
        'roles' is a dict of settings, with keys of role ids as returned by 
        roles(), and values True if the role is explicitly set, False
        if the role is explicitly disabled and None if the role is inherited.
        """
        context = aq_inner(self.context)
        acl_users = getToolByName(context, 'acl_users')
        
        existing_settings = self.existing_role_settings()
        existing_users = set([u['id'] for u in existing_settings
                                if u['type'] == 'user'])        
        empty_roles = dict([(r['id'], False) for r in self.roles()])
        
        info = []
        selected_users = self.selected_users()
        for user_info in selected_users:
            userid = user_info['id']
            if not userid or userid in existing_users:
                continue
            info.append(user_info)            

        return existing_settings + info
    
    @memoize
    def selected_users(self):
        context = aq_inner(self.context)
        acl_users = getToolByName(context, 'acl_users')
        portal_groups = getToolByName(context, 'portal_groups')
        
        empty_roles = dict([(r['id'], False) for r in self.roles()])
        
        info = []
        principal_ids = self.request.form.get('sharing_selected', [])
        if isinstance(principal_ids, (str, unicode)):
            principal_ids = [ principal_ids ]
        group_name = self.request.form.get('group_name', None)
        if group_name:
            principal_ids = [ group_name ]
        for principal_id in principal_ids:
            principal = acl_users.searchPrincipals(id=principal_id)
            if not principal:
                continue
            principal = principal[0]
            if principal['principal_type'] == 'user':
                user = acl_users.getUserById(principal_id)
                roles = empty_roles.copy()
                for r in user.getRoles():
                    if r in roles:
                        roles[r] = 'global'
                info.append(dict(id    = principal_id,
                                 title = user.getProperty('fullname') or user.getId() or principal_id,
                                 type  = 'user',
                                 roles = roles))
            else:
                group = portal_groups.getGroupById(principal_id)
                roles = empty_roles.copy()
                for r in group.getRoles():
                    if r in roles:
                        roles[r] = 'global'                
                info.append(dict(id    = principal_id,
                                 title = group.getGroupTitleOrName(),
                                 type  = 'group',
                                 roles = roles))
        
        return info
