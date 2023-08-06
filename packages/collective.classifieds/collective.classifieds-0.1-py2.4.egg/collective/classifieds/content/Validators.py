import re
from Products.validation.interfaces import ivalidator
from Products.CMFPlone import utils
from zope.i18n import translate

class PhoneValidator:
    """
        Class which provides a simple validation check on a phonenumber
    """
    __implements__ = (ivalidator,)
    def __init__(self, name):
        self.name = name
        
    def __call__(self, value, *args, **kwargs):
        """
            Validates the given value
        """
        if re.match('[0-9\+\-()]+',value):
            return 1
        
        
        return translate(u'classifieds_invalid_phonenumber', domain='classifieds', context=self)