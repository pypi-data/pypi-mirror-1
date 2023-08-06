# -*- coding: utf-8 -*-
#
# File: Classifieds.py
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


Classifieds_schema = BaseBTreeFolderSchema.copy() + \
    schema.copy()


class Classifieds(BaseBTreeFolder, BrowserDefaultMixin):
    """
    """
    security = ClassSecurityInfo()

    implements(interfaces.IClassifieds)

    meta_type = 'Classifieds'
    _at_rename_after_creation = True

    schema = Classifieds_schema

    def getParentNodePath(self):
        """Gets the path of the Organisatie (parent)"""
        return self.getParentNode().getPath();
        
    def getPath(self):
        """Gets the path of the object"""
        path = '/'.join(self.getPhysicalPath());
        return path

    # Methods

registerType(Classifieds, PROJECTNAME)
# end of class Classifieds



