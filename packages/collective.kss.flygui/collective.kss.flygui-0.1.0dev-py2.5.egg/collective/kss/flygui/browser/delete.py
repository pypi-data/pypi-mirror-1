from Products.Five.browser import BrowserView
from zope.app.pagetemplate import ViewPageTemplateFile

class DeletePopup(BrowserView):

    render = ViewPageTemplateFile("templates/delete_popup.pt")

    def __init__(self, context, request, paths):
            # @param paths: List of paths to delete

            super(DeletePopup, self).__init__(context, request)
            self.paths = paths
