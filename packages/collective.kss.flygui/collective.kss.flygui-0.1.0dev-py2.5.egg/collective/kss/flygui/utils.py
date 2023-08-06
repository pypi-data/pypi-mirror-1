from zope.component import queryMultiAdapter
from zope.contentprovider.interfaces import IContentProvider

from plone.memoize import instance
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.permissions import ModifyPortalContent
from Products.CMFCore.permissions import ChangeLocalRoles

from plone.locking.interfaces import ILockable

# Class used to manage additional informations on brain
class ItemManager(object):

    def __init__(self, brain, request):
        self.brain = brain
        self.request = request

    @property
    @instance.memoize
    def obj(self):
        return self.brain.getObject()
    
    @property
    @instance.memoize
    def table_row_class(self):
        return ((self.obj.getObjPositionInParent() + 1) % 2) and 'even' or 'odd'

    @property
    @instance.memoize
    def mtool(self):
        return getToolByName(self.obj, "portal_membership")
    
    @property
    @instance.memoize
    def vtool(self):
        return getToolByName(self.obj, "portal_repository")    

    @property
    @instance.memoize
    def lock_user(self):
        lockable = ILockable(self.obj)
        info = lockable.lock_info()

        if info:
            return info[0]['creator']

        return None

    @instance.memoize
    def canEdit(self):
        # Check if current user is the one who has lock document
        member = self.mtool.getAuthenticatedMember()
        
        if self.lock_user and member.getId() != self.lock_user:
            return False
        
        return self.mtool.checkPermission(ModifyPortalContent, self.obj)
    
    @instance.memoize
    def canModifyLock(self):
        return self.mtool.checkPermission(ModifyPortalContent, self.obj)
    
    @instance.memoize
    def canChangeLocalRoles(self):
        return self.mtool.checkPermission(ChangeLocalRoles, self.obj)

    @instance.memoize
    def isLocked(self):
        lockable = ILockable(self.obj)
        return lockable.locked()
    
    @instance.memoize
    def isVersionable(self):
        return self.vtool.isVersionable(self.obj)

    def renderWorkflow(self):
        provider = queryMultiAdapter((self.obj, self.request, None),
            IContentProvider,
            'flygui.content.menu.workflow.provider')
        
        return provider.render()