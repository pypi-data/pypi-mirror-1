# -*- coding: utf-8 -*-
#
# File: ClassifiedsCategory.py
#
# Copyright (c) 2008 by []
# Generator: ArchGenXML Version 2.1
#            http://plone.org/products/archgenxml
#
# GNU General Public License (GPL)
#

__author__ = """Four Digits <Ralph Jacobs>"""
__docformat__ = 'plaintext'

from AccessControl import ClassSecurityInfo
from Products.Archetypes.atapi import *
from zope.interface import implements
import interfaces

from Products.CMFDynamicViewFTI.browserdefault import BrowserDefaultMixin

from collective.classifieds.config import *



schema = Schema((


),
)



ClassifiedsCategory_schema = BaseBTreeFolderSchema.copy() + \
    schema.copy()



class ClassifiedsCategory(BaseBTreeFolder, BrowserDefaultMixin):
    """
    """
    security = ClassSecurityInfo()

    implements(interfaces.IClassifiedsCategory)

    meta_type = 'ClassifiedsCategory'
    _at_rename_after_creation = True

    schema = ClassifiedsCategory_schema
      
    def getPath(self):
        """Gets the path of the object"""
        path = '/'.join(self.getPhysicalPath());
        return path
    
    def getParentTitle(self):
        """Get parent title"""
        return "%s" % (self.getParentNode().Title())
    # Methods

registerType(ClassifiedsCategory, PROJECTNAME)
# end of class ClassifiedsCategory




