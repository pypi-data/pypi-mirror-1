# -*- coding: utf-8 -*-
try:
    from Products.LinguaPlone.public import *
except ImportError:
    # No multilingual support
    from Products.Archetypes.atapi import *

from jyu.portalview.interfaces import IPortalViewColumnFolder
from jyu.portalview import config
from jyu.portalview.content.schemata import PortalViewColumnFolderSchema

from zope.interface import implements
from zope.component import adapter


class PortalViewColumnFolder(OrderedBaseFolder):
    """ A simple folderish type containing actual portal views """
    
    implements(IPortalViewColumnFolder)
    
    portal_type                 = "Portal View Column Folder"
    schema                      = PortalViewColumnFolderSchema
    _at_rename_after_creation   = True
    
    title       = ATFieldProperty('title')
    description = ATFieldProperty('description')
    width       = ATFieldProperty('width')

registerType(PortalViewColumnFolder, config.PROJECTNAME)
