from Acquisition import aq_inner
from zope.interface import Interface
from zope.interface import implements
from zope.component import getUtility
from zope.component import adapts
from zope.component import queryMultiAdapter
from zope.app.publisher.interfaces.browser import IBrowserMenu
from zope.app.publisher.browser.menu import BrowserMenu
from zope.app.pagetemplate import ViewPageTemplateFile

from Products.CMFCore.utils import getToolByName

from plone.app.contentmenu.interfaces import IContentMenuView
from plone.app.contentmenu.menu import WorkflowSubMenuItem as \
    BaseWorkflowSubMenuItem
from Acquisition import Explicit
from Products.CMFPlone import utils

# FIXME: Use a five or a zope import for ViewPageTemplateFile
#from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile

from interfaces import IWorkflowMenu

class WorkflowMenu(BrowserMenu):
    implements(IWorkflowMenu)

    def getMenuItems(self, context, request):
        """Return menu item entries in a TAL-friendly form."""
        results = []
        context = aq_inner(context)
        context_css_class = 'kssattr-uid-%s' % context.UID()
        wf_tool = getToolByName(context, "portal_workflow")
        workflowActions = wf_tool.listActionInfos(object=context)

        locking_info = queryMultiAdapter((context, request), name='plone_lock_info')
        if locking_info and locking_info.is_locked_for_current_user():
            return []

        for action in workflowActions:
            if action['category'] != 'workflow':
                continue

            cssClass = context_css_class + ' ' + \
                'kssattr-action-%s' % action['id']
            actionUrl = action['url']

            if actionUrl == "":
                actionUrl = '%s/content_status_modify?workflow_action=%s' % (context.absolute_url(), action['id'])

            description = ''

            transition = action.get('transition', None)
            if transition is not None:
                description = transition.description

            if action['allowed']:
                results.append({ 'title'        : action['title'],
                                 'description'  : description,
                                 'action'       : actionUrl,
                                 'selected'     : False,
                                 'icon'         : None,
                                 'extra'        : {'separator' : None, 'class' : cssClass},
                                 'submenu'      : None,
                                 })
        return results

class WorkflowSubMenuItem(BaseWorkflowSubMenuItem):

    title = u''
    submenuId = "flygui.content.menu.workflow"

    @property
    def extra(self):
        state = self.context_state.workflow_state()
        stateTitle = self._currentStateTitle()
        return {'id'         : 'content-menu-workflow-%s' % \
                                self.context.UID(),
                'class'      : 'state-%s' % state,
                'state'      : state,
                'stateTitle' : stateTitle,}

class WorkflowMenuProvider(Explicit):
    """Content menu provider for the "view" tab: displays the menu
    """

    implements(IContentMenuView)

    def __init__(self, context, request, view):
        self.__parent__ = view
        self.view = view
        self.context = context
        self.request = request

    # From IContentProvider

    def update(self):
        pass

    #render = ZopeTwoPageTemplateFile('templates/menu.pt')
    render = ViewPageTemplateFile('templates/menu.pt')
    # From IContentMenuView

    def available(self):
        return True

    def menu(self):
        menu = getUtility(IBrowserMenu,
                          name='flygui.content.menu')
        items = menu.getMenuItems(self.context, self.request)
        return items[0]