from zope.component import getMultiAdapter

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFPlone import PloneMessageFactory as plone_i18n

from plone.app.workflow.browser import kss_sharing

class KSSSharingView(kss_sharing.KSSSharingView):
    """KSS view for sharing page.
    """
    template = ViewPageTemplateFile('templates/sharing.pt')
    
    def createGroup(self, group_name):
        sharing = getMultiAdapter((self.context, self.request,), name="sharing")
        group_users = self.request.form.get('sharing_selected', [])
        if isinstance(group_users, (str, unicode)):
            group_users = [ group_users ]
        
        if sharing.createGroup(group_name, group_users):
            msg = plone_i18n(u'Group ${name} has been added.', mapping={u'name' : group_name})
            msg = self.context.translate(msg)
            msg = msg.encode('utf')
            self.getCommandSet('plone').issuePortalMessage(msg)            
            return self.updateSharingInfo(search_term=group_name)
        else:
            msg = plone_i18n(u'Could not add group ${name}, perhaps a user or group with '
                             u'this name already exists.', mapping={u'name' : group_name})
            msg = self.context.translate(msg)
            msg = msg.encode('utf')            
            self.getCommandSet('plone').issuePortalMessage(msg, msgtype='error')
            return self.updateUserSelection()
    
    def updateUserSelection(self):
        sharing = getMultiAdapter((self.context, self.request,), name="sharing")
        sharing.users_selection = sharing.selected_users()
        
        ksscore = self.getCommandSet('core')
        the_id = 'user-selection'
        macro = self.template.macros[the_id]
        res = self.macro_wrapper(the_macro=macro, instance=self.context, view=sharing)
        ksscore.replaceHTML(ksscore.getHtmlIdSelector(the_id), res)

        return self.render()