__author__ = """Four Digits <unknown>"""
__docformat__ = 'plaintext'

import logging
logger = logging.getLogger('Classifieds: setuphandlers')
from collective.classifieds.config import PROJECTNAME
from collective.classifieds.config import DEPENDENCIES
import os
from config import product_globals
from Globals import package_home
from Products.CMFCore.utils import getToolByName
import transaction

from OFS.CopySupport import CopyContainer

def isNotClassifiedsProfile(context):
    return context.readDataFile("Classifieds_marker.txt") is None

def updateRoleMappings(context):
    """after workflow changed update the roles mapping. this is like pressing
    the button 'Update Security Setting' and portal_workflow"""

    # only for classifieds types
    if isNotClassifiedsProfile(context): return
    wft = getToolByName(context.getSite(), 'portal_workflow')
    wft.updateRoleMappings()

def postInstall(context):
    """Called as at the end of the setup process. """
    # the right place for your custom code
    if isNotClassifiedsProfile(context): return
    site = context.getSite()
