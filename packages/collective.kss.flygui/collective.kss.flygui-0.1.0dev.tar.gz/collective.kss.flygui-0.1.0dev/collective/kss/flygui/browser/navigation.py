from zope.interface import implements
from zope.interface import Interface
from zope.formlib.form import Fields
from zope.component import adapts, getMultiAdapter, getUtility


from Acquisition import aq_inner

from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import utils

from plone.memoize.instance import memoize

from plone.app.form.widgets.uberselectionwidget import UberSelectionWidget
from plone.app.portlets.utils import assignment_from_key
from plone.app.portlets.portlets.base import AddForm as BaseAddForm
from plone.app.portlets.portlets.base import EditForm as BaseEditForm
from plone.app.portlets.portlets.base import Assignment as BaseAssignment
from plone.app.portlets.portlets.navigation import Renderer as BaseRenderer
from plone.app.portlets.portlets.navigation import NavtreeStrategy
from plone.app.layout.navigation.interfaces import INavigationQueryBuilder
from plone.app.layout.navigation.interfaces import INavtreeStrategy
from plone.app.layout.navigation.root import getNavigationRoot
from plone.app.layout.navigation.navtree import buildFolderTree
from plone.portlets.utils import unhashPortletInfo
from plone.portlets.interfaces import IPortletManager
from plone.app.kss.plonekssview import PloneKSSView

from collective.kss.flygui import MessageFactory as _
from collective.kss.flygui.utils import ItemManager
from interfaces import INavigationPortlet



def finalizeNavTree(data, request):
    opened_branches = request.get('opened_branches', '').split(',');
    def walkNavTree(root):
        for node in root['children']:
            node['item_manager'] = ItemManager(node['item'], request)        
            walkNavTree(node)
    
    walkNavTree(data)

class Assignment(BaseAssignment):
    implements(INavigationPortlet)

    title = _(u'Extended Navigation')
    name = u""
    root = None
    currentFolderOnly = False
    includeTop = False
    topLevel = 1
    bottomLevel = 0
    portalTypes = ()

    def __init__(self, name=u"", root=None, currentFolderOnly=False,
                 includeTop=False, topLevel=1, bottomLevel=0, portalTypes=()):
        self.name = name
        self.root = root
        self.currentFolderOnly = currentFolderOnly
        self.includeTop = includeTop
        self.topLevel = topLevel
        self.bottomLevel = bottomLevel
        self.portalTypes = portalTypes

class Renderer(BaseRenderer):
    _template = ViewPageTemplateFile('templates/navigation.pt')
    recurse = ViewPageTemplateFile('templates/navigation_recurse.pt')
    

    
    
    @memoize
    def getNavTree(self, _marker=[]):
        context = aq_inner(self.context)
        
        # Special case - if the root is supposed to be pruned, we need to
        # abort here

        queryBuilder = getMultiAdapter((context, self.data), INavigationQueryBuilder)
        strategy = getMultiAdapter((context, self.data), INavtreeStrategy)

        data = buildFolderTree(context, obj=context, query=queryBuilder(), strategy=strategy)
        finalizeNavTree(data, self.request)
        return data

class AddForm(BaseAddForm):
    form_fields = Fields(INavigationPortlet)
    form_fields['root'].custom_widget = UberSelectionWidget
    label = _(u"Add Extended Navigation Portlet")
    description = _(u"This portlet display a navigation tree.")

    def create(self, data):
        return Assignment(
            name=data.get('name', u""),
            root=data.get('root', u""),
            currentFolderOnly=data.get('currentFolderOnly', False),
            topLevel=data.get('topLevel', 0),
            bottomLevel=data.get('bottomLevel', 0),
            portalTypes=data.get('portalTypes', ()),
            )

class EditForm(BaseEditForm):
    form_fields = Fields(INavigationPortlet)
    form_fields['root'].custom_widget = UberSelectionWidget
    label = _(u"Edit Extended Navigation Portlet")
    description = _(u"This portlet display a navigation tree.")

class NavBranch(PloneKSSView):
    recurse = ViewPageTemplateFile('templates/navigation_recurse.pt')
    
    @memoize
    def getNavTree(self, level, context_uid, portlethash):
        info = unhashPortletInfo(portlethash) 
        manager = getUtility(IPortletManager, info['manager'])
        assignment = assignment_from_key(context = self.context, 
                                         manager_name = info['manager'], 
                                         category = info['category'],
                                         key = info['key'],
                                         name = info['name'])   
        
        assignment = Assignment(
            name=assignment.name, 
            root=assignment.root,
            currentFolderOnly=True,
            includeTop=assignment.includeTop,
            topLevel=assignment.topLevel,
            bottomLevel=assignment.bottomLevel, 
            portalTypes=assignment.portalTypes
        )
        atool = getToolByName(self.context, 'archetype_tool')
        context = atool.getObject(context_uid)
        
        query = getMultiAdapter((context, assignment), INavigationQueryBuilder)()
        strategy = getMultiAdapter((context, assignment), INavtreeStrategy)        
        data = buildFolderTree(context, obj=context, query=query, strategy=strategy)
        
        finalizeNavTree(data, self.request)
        return data
    
    def openBranch(self, level, context_uid, portlethash):
        core = self.getCommandSet('core')
        uid_selector = '.kssattr-uid-%s' % context_uid
        item_selector = '#portal-column-one .portletNavigationTree li span%s' % uid_selector
        
        data = self.getNavTree(level, context_uid, portlethash)
        render = self.recurse(children=data.get('children', []), bottomLevel=1)     
        if not render.strip():
            render = '<li class="discreet">(empty)</li>'        
        core.replaceInnerHTML('%s + ul' % item_selector, render)
        core.commands.addCommand('flygui.navigator.openBranch', item_selector)
        return self.render()
