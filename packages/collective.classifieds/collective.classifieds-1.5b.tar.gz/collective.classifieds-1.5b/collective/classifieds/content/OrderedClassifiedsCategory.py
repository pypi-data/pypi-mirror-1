__author__ = """Four Digits <Ralph Jacobs>"""
__docformat__ = 'plaintext'

from AccessControl import ClassSecurityInfo
from Products.Archetypes.atapi import *
from zope.interface import implements
import interfaces
from Products.CMFCore.utils import getToolByName

from Products.CMFDynamicViewFTI.browserdefault import BrowserDefaultMixin
from collective.classifieds.config import *

from Products.ATContentTypes.content.folder import ATFolderSchema, ATFolder

schema = Schema((
    ImageField(
        name='categoryimage',
        widget=ImageField._properties['widget'](
            label="Category image",
            description="Image which represents the category",
            label_msgid="classifieds_classifiedscategory_categoryimage",
            description_msgid="classifieds_classifiedscategory_categoryimage_description",
            i18n_domain='classifieds',
        ),
        storage=AttributeStorage(),
        max_size=(768,768),
        sizes= {'large'   : (768, 768),
                   'preview' : (400, 400),
                   'mini'    : (200, 200),
                   'thumb'   : (128, 128),
                   'tile'    :  (64, 64),
                   'icon'    :  (32, 32),
                   'listing' :  (16, 16),
                  },
    ),    

),
)

OrderedClassifiedsCategory_schema = ATFolderSchema.copy() + \
    schema.copy()

class OrderedClassifiedsCategory(ATFolder):
    """
        Category which can contain Classifieds (such as books), Ordered version
    """
    security = ClassSecurityInfo()

    implements(interfaces.IOrderedClassifiedsCategory)

    meta_type = 'OrderedClassifiedsCategory'
    _at_rename_after_creation = True

    schema = OrderedClassifiedsCategory_schema

    def getPath(self):
        """Gets the path of the object"""
        path = '/'.join(self.getPhysicalPath());
        return path

    def getParentTitle(self):
        """Get parent title"""
        return "%s" % (self.getParentNode().Title())
        
    def hasImage(self):
        """checks if the category has a image"""
        if self.getCategoryimage():
            return True

        return False
    
    def getImageTile(self, **kwargs):
        """Get image tile url, relative to plone site."""
        if self.hasImage():
            imgtileurl = self.getCategoryimage().absolute_url(1) + '_tile'
            portal_url = getToolByName(self, 'portal_url').getPortalObject().absolute_url(1)
            imgtileurl = imgtileurl.replace(portal_url, '')
            return imgtileurl
        return ''
    
    # Methods

registerType(OrderedClassifiedsCategory, PROJECTNAME)
# end of class OrderedClassifiedsCategory
