import urllib

from OFS import Moniker
from OFS.CopySupport import _cb_decode

from zope.component import getMultiAdapter
from zope.app.pagetemplate import ViewPageTemplateFile

from Products.CMFCore.utils import getToolByName

from Products.ATContentTypes.interface import IATTopic

from plone.memoize import instance
from plone.app.content.browser import foldercontents
from plone.app.content.browser.tableview import Table as BaseTable

from collective.kss.flygui.utils import ItemManager


class FolderContentsView(foldercontents.FolderContentsView):
    """ """

    def contents_table(self):
        table = FolderContentsTable(self.context, self.request)
        return table.render()    

class Table(BaseTable):
    """
    """

    def __init__(self, context, request, base_url, view_url, items,
                 show_sort_column=False, buttons=[]):
        BaseTable.__init__(self, request, base_url, view_url, items,
                           show_sort_column, buttons)
        self.context = context
        self.portal_state = getMultiAdapter((self.context, self.request),
            name=u'plone_portal_state')        
        self.portal = self.portal_state.portal()
        self.portal_url = self.portal.absolute_url()
        self.sort_on = request.get('sort_on', 
                                   FolderContentsTable.default_sort_on)        
        self.clipboard = self.getClipboard()  

    batching = ViewPageTemplateFile("templates/batching.pt")
    render = ViewPageTemplateFile('templates/table.pt')
    row = ViewPageTemplateFile('templates/table_row.pt')
    
    def render_row(self, instance):
        return self.row(instance)
    
    def getClipboard(self):
        # List of objects in the clip board
        try:    cp=_cb_decode(self.request['__cp'])
        except: return -1, []
        oblist=[]
        
        app = self.context.getPhysicalRoot()
        for mdata in cp[1]:
            m = Moniker.loadMoniker(mdata)
            oblist.append(m.bind(app))
        return cp[0], oblist
    
    def isCopied(self, obj):
        return self.clipboard[0] == 0 and obj in self.clipboard[1]       
    
    def isCut(self, obj):
        return self.clipboard[0] == 1 and obj in self.clipboard[1]


class FolderContentsTable(foldercontents.FolderContentsTable):
    """ """
    default_sort_on = 'getObjPositionInParent'
    
    def __init__(self, context, request, contentFilter={}):
        self.context = context
        self.request = request
        contentFilter['sort_on'] = contentFilter.get('sort_on', self.default_sort_on)
        self.contentFilter = contentFilter
        
        url = self.context.absolute_url()
        view_url = url + '/@@folder_contents'
        self.table = Table(self.context, request, url, view_url, self.items,
                           show_sort_column=self.show_sort_column,
                           buttons=self.buttons)        

    def render_row(self, view):
        return self.table.render_row(view)

    @property
    @instance.memoize
    def items(self):
        """ """
        plone_utils = getToolByName(self.context, 'plone_utils')
        plone_view = getMultiAdapter((self.context, self.request), name=u'plone')
        portal_workflow = getToolByName(self.context, 'portal_workflow')
        portal_properties = getToolByName(self.context, 'portal_properties')
        site_properties = portal_properties.site_properties
        
        use_view_action = site_properties.getProperty('typesUseViewActionInListings', ())        
        browser_default = self.context.browserDefault()
                
        if IATTopic.providedBy(self.context):
            contentsMethod = self.context.queryCatalog
        else:
            contentsMethod = self.context.getFolderContents
        
        results = []
        for i, obj in enumerate(contentsMethod(self.contentFilter)):
            url = obj.getURL()
            path = obj.getPath or "/".join(obj.getPhysicalPath())
            icon = plone_view.getIcon(obj);
            
            type_class = 'contenttype-' + plone_utils.normalizeString(
                obj.portal_type)

            review_state = obj.review_state
            state_class = 'state-' + plone_utils.normalizeString(review_state)
            relative_url = obj.getURL(relative=True)
            obj_type = obj.portal_type

            modified = plone_view.toLocalizedTime(
                obj.ModificationDate, long_format=1)
            
            if obj_type in use_view_action:
                view_url = url + '/view'
            elif obj.is_folderish:
                view_url = url + "/folder_contents"              
            else:
                view_url = url

            is_browser_default = len(browser_default[1]) == 1 and (
                obj.id == browser_default[1][0])
                                 
            results.append(dict(
                url = url,
                id  = obj.getId,
                quoted_id = urllib.quote_plus(obj.getId),
                path = path,
                title_or_id = obj.pretty_title_or_id(),
                description = obj.Description,
                obj_type = obj_type,
                size = obj.getObjSize,
                modified = modified,
                icon = icon.html_tag(),
                type_class = type_class,
                wf_state = review_state,
                state_title = portal_workflow.getTitleForStateOnType(review_state,
                                                           obj_type),
                state_class = state_class,
                is_browser_default = is_browser_default,
                folderish = obj.is_folderish,
                relative_url = relative_url,
                view_url = view_url,
                is_expired = self.context.isExpired(obj),
                brain = obj,
                uid = obj.UID,
                item_manager=ItemManager(obj, self.request),
            ))
        return results


