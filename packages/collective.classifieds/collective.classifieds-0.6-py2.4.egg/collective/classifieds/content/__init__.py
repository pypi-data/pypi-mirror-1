__author__ = """Four Digits <Ralph Jacobs>"""
__docformat__ = 'plaintext'


# Subpackages
from Products.validation import validation

from Validators import FloatValidator
validation.register(FloatValidator('isFloat'))

# Additional

# Classes
import ClassifiedsCategory
import Classifieds
import Classified
