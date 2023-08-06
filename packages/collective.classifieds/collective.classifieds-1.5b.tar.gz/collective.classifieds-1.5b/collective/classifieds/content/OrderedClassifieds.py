__author__ = """Four Digits <Ralph Jacobs>"""
__docformat__ = 'plaintext'

from AccessControl import ClassSecurityInfo
from Products.Archetypes.atapi import *
from zope.interface import implements
import interfaces

from Products.CMFDynamicViewFTI.browserdefault import BrowserDefaultMixin
from collective.classifieds.config import *

from Products.ATContentTypes.content.folder import ATFolderSchema, ATFolder


schema = Schema((

),
)

OrderedClassifieds_schema = ATFolderSchema.copy() + \
    schema.copy()

class OrderedClassifieds(ATFolder):
    """
        Container which can contain Categories and Classifieds (Ordered)
    """
    security = ClassSecurityInfo()

    implements(interfaces.IOrderedClassifieds)

    meta_type = 'OrderedClassifieds'
    _at_rename_after_creation = True

    schema = OrderedClassifieds_schema

    def getPath(self):
        """Gets the path of the object"""
        path = '/'.join(self.getPhysicalPath());
        return path

registerType(OrderedClassifieds, PROJECTNAME)
# end of class Classifieds
