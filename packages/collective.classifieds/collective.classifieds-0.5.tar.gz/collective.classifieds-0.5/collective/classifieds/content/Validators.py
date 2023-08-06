import re
from Products.validation.interfaces import ivalidator
from Products.CMFPlone import utils
from zope.i18n import translate

class FloatValidator:
    """
       Class which provides us a simple validation check on a float 
    """
    __implements__ = (ivalidator,)
    def __init__(self, name):
        self.name = name

    def __call__(self, value, *args, **kwargs):
        """
            Validates the given value
        """
        FLOAT_RE = "^([+-]?)(?=\d|\.\d)\d*(\.\d*)?([Ee]([+-]?\d+))?$"

        if re.match(FLOAT_RE,value):
            return 1
        
        return translate(u'classifieds_invalid_float', domain='classifieds', context=self)