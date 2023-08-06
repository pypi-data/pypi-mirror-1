# -*- coding: utf-8 -*-
try:
    from Products.LinguaPlone.public import *
except ImportError:
    # No multilingual support
    from Products.Archetypes.atapi import *

from Acquisition import aq_inner, aq_parent

from Products.Archetypes.interfaces import IObjectInitializedEvent
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import _createObjectByType

from jyu.portalview.interfaces import IPortalView
from jyu.portalview.config import PROJECTNAME, COLUMNS
from jyu.portalview.content.schemata import PortalViewSchema

from zope.interface import implements
from zope.component import adapter, getUtility, getMultiAdapter

from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import ILocalPortletAssignable
from plone.portlets.interfaces import ILocalPortletAssignmentManager
from plone.portlets.constants import CONTEXT_CATEGORY
from plone.portlets.constants import GROUP_CATEGORY
from plone.portlets.constants import CONTENT_TYPE_CATEGORY

from jyu.portalview import PortalViewMessageFactory as _

from zope.i18n import translate

class PortalView(OrderedBaseFolder):
    """ A content type, which displays content in a portal like aggregating view
    """
   
    implements(IPortalView, ILocalPortletAssignable)
    
    portal_type                 = "Portal View"
    schema                      = PortalViewSchema
    _at_rename_after_creation   = True
    
    title       = ATFieldProperty('title')
    description = ATFieldProperty('description')
    css         = ATFieldProperty('css')

    menuBarEnabled    = ATFieldProperty('menuBarEnabled')
    breadCrumbsHidden = ATFieldProperty('breadCrumbsHidden')
    menuBarContents   = ATFieldProperty('menuBarContents')

registerType(PortalView, PROJECTNAME)


@adapter(IPortalView, IObjectInitializedEvent)
def add_default_contents(obj, event):
    """ Add default folder structure under Portal View content type """

    widths = {
        2: ['80', '20'],
        3: ['30', '30', '20'],
        4: ['25', '25', '25', '25'],
    }[COLUMNS]

    ids = {
        2: [_(u"left"), _(u"right")],
        3: [_(u"left"), _(u"middle"), _(u"right")],
        4: [_(u"left"), _(u"center-left"), _(u"center-right"), _(u"right")],
    }[COLUMNS]

    titles = {
        2: [_(u"Left Column"), _(u"Right Column")],
        3: [_(u"Left Column"), _(u"Middle Column"), _(u"Right Column")],
        4: [_(u"Left Column"), _(u"Center-Left Column"), _(u"Center-Right Column"), _(u"Right Column")],
    }[COLUMNS]

    lang = obj.REQUEST.get('LANGUAGE', 'en')

    # We don't need to bug actual users with things starting from zero
    for column in range(1, COLUMNS + 1):
        id = translate(msgid=ids[column - 1], domain="jyu.portalview", target_language=lang)
        title = translate(msgid=titles[column - 1], domain="jyu.portalview", target_language=lang)
        width = widths[column - 1]
        
        _createObjectByType('Portal View Column Folder', obj, id)
        created_obj = obj[id]
        created_obj.setTitle(title)
        created_obj.setWidth(width)
        
        membershipTool = getToolByName(obj, 'portal_membership')
        if membershipTool.checkPermission('Review portal content', obj):
            workflowTool = getToolByName(obj, 'portal_workflow')
            workflowTool.doActionFor(created_obj, "publish")

        created_obj.reindexObject()

        _createObjectByType('Document', created_obj, "sample-content")
        created_obj = created_obj["sample-content"]
        created_obj.setTitle(title)
        
        membershipTool = getToolByName(obj, 'portal_membership')
        if membershipTool.checkPermission('Review portal content', obj):
            workflowTool = getToolByName(obj, 'portal_workflow')
            workflowTool.doActionFor(created_obj, "publish")      
        
        created_obj.reindexObject()

    if not obj.getCSS():
        obj.setCSS(translate(msgid="default_css", domain="jyu.portalview", default=u"""\
#portalview-column-left .portletHeader {
  background-color: lightyellow;
}""", target_language=lang))

    if not obj.getMenuBarContents():
        obj.setMenuBarContents(translate(msgid="default_menubar", domain="jyu.portalview", default=u"""\
<ul>
  <li><a href="">Regular link</a></li>
  <li><a href="">1. Menu</a>
     <ul>
       <li><a href="">1.1 Menu Item</a></li>
       <li><a href="">1.2 Menu Item</a></li>
       <li></li>
       <li><a href="">1.3 Menu Item</a></li>
     </ul>
   </li>
   <li><a href="">2. Menu</a>
     <ul>
       <li><a href="">2.1 Menu Item</a></li>
       <li><a href="">2.2 Menu Item</a></li>
       <li></li>
       <li><a href="">2.3 Menu Item</a></li>
     </ul>
   </li>
</ul>""", target_language=lang))

        
@adapter(IPortalView, IObjectInitializedEvent)
def blacklist_portlets(obj, event):
    """ Blacklists all parent portlets """

    parent = aq_parent(aq_inner(obj))

    if IPortalView.providedBy(parent):
        return

    # Blacklist all the other portlets
    column = getUtility(IPortletManager, name = u'plone.rightcolumn')
    blacklist = getMultiAdapter((obj, column), ILocalPortletAssignmentManager)
    blacklist.setBlacklistStatus(CONTEXT_CATEGORY, True)
    blacklist.setBlacklistStatus(GROUP_CATEGORY, True)
    blacklist.setBlacklistStatus(CONTENT_TYPE_CATEGORY, True)

    column = getUtility(IPortletManager, name = u'plone.leftcolumn')
    blacklist = getMultiAdapter((obj, column), ILocalPortletAssignmentManager)
    blacklist.setBlacklistStatus(CONTEXT_CATEGORY, True)
    blacklist.setBlacklistStatus(GROUP_CATEGORY, True)
    blacklist.setBlacklistStatus(CONTENT_TYPE_CATEGORY, True)
