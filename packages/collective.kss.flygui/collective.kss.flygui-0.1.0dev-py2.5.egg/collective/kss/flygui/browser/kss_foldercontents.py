from Acquisition import aq_inner, aq_parent

import transaction

from Products.CMFCore.utils import getToolByName
from Products.CMFCore.permissions import ModifyPortalContent

from plone.app.kss.plonekssview import PloneKSSView
from plone.locking.interfaces import ILockable
from plone.app.kss.portlets import PortletReloader

from interfaces import INavigationPortlet
from lock import LockPopup
from delete import DeletePopup
from foldercontents import FolderContentsTable

class FolderContentsKSSView(PloneKSSView):
    """ """

    def delete_and_update_table(self, paths=None,  confirm='False'):

        # Get list of paths to be deleted
        core = self.getCommandSet('core')
        del_paths = self.context.request.get('paths', paths)

        if del_paths and confirm == 'False':
            # User should confirm the deletion
            # Open popup to alert user if he is sure about document deletion
            delete_popup = DeletePopup(self.context, self.request, del_paths)
            command = core.commands.addCommand('flygui.modal.open')
            command.addParam('containerId', 'delete-popup')
            core.replaceInnerHTML('#delete-popup', delete_popup.render())
            return self.render()

        # Delete objects
        self.context.folder_delete()

        # Execute some kss commands
        self.issueAllPortalMessages()
        self.cancelRedirect()

        if not del_paths:
            # User needs to select at less one item to delete
            return self.render()

        #self.reloadNavTreePortlet()
        self.deleteNavTreeItems()

        # Then close popup and refresh folder_contents view
        command = core.commands.addCommand('flygui.modal.close')
        return self.update_table()
    
    
    def cut_and_update_table(self, paths=None):
        # Cut objects
        self.context.folder_cut()

        # Execute some kss commands
        self.issueAllPortalMessages()
        self.cancelRedirect()

        if not paths:
            # User needs to select at less one item to delete
            return self.render()
        
        return self.update_table()
        
    def copy_and_update_table(self, paths=None):
        # Cut objects
        self.context.folder_copy()

        # Execute some kss commands
        self.issueAllPortalMessages()
        self.cancelRedirect()

        if not paths:
            # User needs to select at less one item to delete
            return self.render()
        
        return self.update_table()
    
    def paste_and_update_table(self):
        # Paste objects
        self.context.folder_paste()

        # Execute some kss commands
        self.issueAllPortalMessages()
        self.cancelRedirect()
        
        return self.update_table() 
    
    def update_status_and_update_table(self, uid, action):
        # Get object
        atool = getToolByName(self.context, 'archetype_tool')
        obj = atool.getObject(uid)

        # Update object status
        obj.content_status_modify(action)

        # Execute some kss commands
        self.issueAllPortalMessages()
        self.cancelRedirect()

        self.updateNavTreeItem(uid)

        # Then refresh folder_contents view
        return self.update_rows([uid])

    def lock_and_update_table(self, uid):
        # Get object
        atool = getToolByName(self.context, 'archetype_tool')
        obj = atool.getObject(uid)

        # Lock it
        lockable = ILockable(obj)
        lockable.lock()

        self.lockNavTreeItem(uid)

        # Then refresh folder_contents view
        return self.update_rows([uid])

    def force_unlock_and_update_table(self, uid):
        # Get object
        atool = getToolByName(self.context, 'archetype_tool')
        obj = atool.getObject(uid)

        # Lock it
        lockable = ILockable(obj)

        # Unlock content
        lockable.unlock()

        # Close popup
        core = self.getCommandSet('core')
        command = core.commands.addCommand('flygui.modal.close')

        self.unlockNavTreeItem(uid)

        # Then refresh folder_contents view
        return self.update_rows([uid])

    def unlock_and_update_table(self, uid, close_popup=False):
        # Get object
        atool = getToolByName(self.context, 'archetype_tool')
        obj = atool.getObject(uid)

        # Lock it
        lockable = ILockable(obj)

        # Check if current user is the one who has lock document
        mtool = getToolByName(self.context, 'portal_membership')
        member = mtool.getAuthenticatedMember()
        info = lockable.lock_info()

        if info and member.getId() == info[0]['creator']:
            # Unlock content
            lockable.unlock()
            self.unlockNavTreeItem(uid)
            # Then refresh folder_contents view
            return self.update_rows([uid])

        # Open popup to alert user this document is locked by another one
        lock_popup = LockPopup(self.context, self.request, uid)
        core = self.getCommandSet('core')        
        command = core.commands.addCommand('flygui.modal.open')
        command.addParam('containerId', 'lock-info-popup')
        core.replaceInnerHTML('#lock-info-popup', lock_popup.render())
        return self.render()

    def update_rows(self, uids):
        table = FolderContentsTable(self.context, self.request, 
                                    contentFilter={'UID': uids})
        return self.replace_rows(table, uids)
    
    def replace_rows(self, table, uids):
        core = self.getCommandSet('core')
        for uid in uids:
            uid_selector = '.kssattr-uid-%s' % uid
            core.replaceHTML('#listing-table tr%s' % uid_selector, 
                             table.render_row(self))
        
        command = core.commands.addCommand('flygui.initializeMenus')
        return self.render()
    
    def update_table(self, pagenumber='1', sort_on=None):
        filter = {'sort_on':    self.request.get('sort_on', sort_on), 
                  'pagenumber': self.request.get('pagenumber', pagenumber) }
        table = FolderContentsTable(self.context, self.request,
                                    contentFilter=filter)
        return self.replace_table(table)

    def replace_table(self, table):
        core = self.getCommandSet('core')
        core.replaceInnerHTML('#folderlisting-main-table', table.render())
        command = core.commands.addCommand('flygui.initializeMenus')
        return self.render()

    def moveFiles(self, uids, targetUID, pagenumber='1'):
        if targetUID in uids:
            # Cannot copy an object into itself
            return self.render()

        atool = getToolByName(self.context, 'archetype_tool')
        if targetUID == 'root':
            target = getToolByName(self.context, 'portal_url').getPortalObject()
        else:
            target = atool.getObject(targetUID)

        if isinstance(uids, str):
            uids = uids.split(',')

        for uid in uids:
            obj = atool.getObject(uid)
            container = aq_parent(aq_inner(obj))
            cb = container.manage_cutObjects(ids=[obj.getId()])
            target.manage_pasteObjects(cb)

        self.update_table(pagenumber)

        core = self.getCommandSet('core')

        #self.deleteNavTreeItems(uids)
        #item_selector = self.getNavTreeBranchSelector(targetUID)
        #command = core.commands.addCommand('flygui.navigator.loadBranch', '%s > img' % item_selector)
        #command.addParam('selector', item_selector)

        command = core.commands.addCommand('flygui.navigator.moveFiles')
        command.addParam('uids', ','.join(uids))
        command.addParam('targetUID', targetUID)
        return self.render()

    def updateNavTreeItem(self, uid):
        # Get object
        atool = getToolByName(self.context, 'archetype_tool')
        obj = atool.getObject(uid)

        # Get lockable
        lockable = ILockable(obj)
        info = lockable.lock_info()

        # Check if current user is the one who has lock document
        mtool = getToolByName(self.context, 'portal_membership')
        member = mtool.getAuthenticatedMember()
        lock_user = info and info[0]['creator'] or None
        is_locker = (lock_user and member.getId() != lock_user)
        canEdit = mtool.checkPermission(ModifyPortalContent, obj)

        if is_locker or canEdit:
            self.unlockNavTreeItem(uid)
        else:
            self.lockNavTreeItem(uid)

    def reloadNavTreePortlet(self):
        portletReloader = PortletReloader(self)
        portletReloader.reloadPortletsByInterface(INavigationPortlet)

    def lockNavTreeItem(self, uid):
        core = self.getCommandSet('core')
        item_selector = self.getNavTreeBranchSelector(uid)
        core.commands.addCommand('flygui.navigator.lockNavTreeItem', item_selector)

    def unlockNavTreeItem(self, uid):
        core = self.getCommandSet('core')
        item_selector = self.getNavTreeBranchSelector(uid)
        core.commands.addCommand('flygui.navigator.unlockNavTreeItem', item_selector)

    def deleteNavTreeItems(self, uids=None):
        core = self.getCommandSet('core')
        uids = uids and ','.join(uids) or self.request.get('uids', '')
        command = core.commands.addCommand('flygui.navigator.deleteNavTreeItems')
        command.addParam('uids', uids)

    def getNavTreeBranchSelector(self, uid):
        uid_selector = '.kssattr-uid-%s' % uid
        return '#portal-column-one .portletNavigationTree li span%s' % uid_selector



