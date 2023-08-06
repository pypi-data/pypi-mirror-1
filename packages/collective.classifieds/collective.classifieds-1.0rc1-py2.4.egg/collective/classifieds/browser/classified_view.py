__author__ = """Four Digits <Ralph Jacobs>"""
__docformat__ = 'plaintext'

from zope import interface
from zope import component
from Products.CMFPlone import utils
from Products.Five import BrowserView
from zope.interface import implements
from collective.classifieds.content.Classifieds import Classifieds
from Products.CMFDynamicViewFTI.browserdefault import BrowserDefaultMixin

class classified_view(BrowserView):
    """
        BrowserView for classified
    """
