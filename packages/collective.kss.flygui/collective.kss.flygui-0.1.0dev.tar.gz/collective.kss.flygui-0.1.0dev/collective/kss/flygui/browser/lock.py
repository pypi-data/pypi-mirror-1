from Products.Five.browser import BrowserView
from zope.app.pagetemplate import ViewPageTemplateFile

from Products.CMFCore.utils import getToolByName

from plone.memoize import instance
from plone.locking.interfaces import ILockable

class LockPopup(BrowserView):

    render = ViewPageTemplateFile("templates/lock_popup.pt")

    def __init__(self, context, request, uid):
            super(LockPopup, self).__init__(context, request)
            self.uid = uid

    def getLockedObject(self):
        # Get object
        atool = getToolByName(self.context, "archetype_tool")
        return atool.getObject(self.uid)

    def getLockInfo(self):
        # Get lock information
        obj = self.getLockedObject()
        lockable = ILockable(obj)
        info = lockable.lock_info()

        # Returns only the first lock information
        return info[0]