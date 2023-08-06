from zope.interface import directlyProvides
from zope.interface import Interface
from zope.schema import Tuple
from zope.schema import Choice
from zope.app.publisher.interfaces.browser import IMenuItemType
from zope.app.publisher.interfaces.browser import IBrowserMenu

from plone.app.portlets.portlets.navigation import INavigationPortlet as \
    IBaseNavigationPortlet

from collective.kss.flygui import MessageFactory as _

class IContentMenuItem(Interface):
    """Special menu item type for Plone's content menu."""

directlyProvides(IContentMenuItem, IMenuItemType)

class IWorkflowMenu(IBrowserMenu):
    """The workflow menu.

    This gets its menu items from the list of possible transitions in
    portal_workflow.
    """

class IFolderCommands(Interface):
    """Interface for KSS Commands to deal with folder contents"""
    

class INavigationPortlet(IBaseNavigationPortlet):
    """Extended properties for extended navigation portlet
    """

    portalTypes = Tuple(
        title=_(u"Portal types"),
        description=_(u"Select portal types to show"),
        default=(),
        required=False,
        value_type=Choice(
            vocabulary="flygui.vocabulary.portal_types"),
        )