# -*- coding: utf-8 -*-
#
# File: setuphandlers.py
#
# Copyright (c) 2008 by Opkode CC
# Generator: ArchGenXML Version 2.0
#            http://plone.org/products/archgenxml
#
# GNU General Public License (GPL)
#

__author__ = """JC Brand <jc@opkode.co.za>"""
__docformat__ = 'plaintext'


import logging
logger = logging.getLogger('dublettefinder: setuphandlers')
# XXX: Archgen egg compatibility bug...
# from Products.dublettefinder.config import PROJECTNAME
# from Products.dublettefinder.config import DEPENDENCIES
import os
from Products.CMFCore.utils import getToolByName
import transaction
##code-section HEAD
from slc.dublettefinder.interfaces import IDubletteFinderConfiguration
from slc.dublettefinder.config import DubletteFinderConfiguration
##/code-section HEAD

def isNotdublettefinderProfile(context):
    return context.readDataFile("dublettefinder_marker.txt") is None


# commented out. If the product is reinstalled with a large database, update role mappings takes ages.
#def updateRoleMappings(context):
#    """after workflow changed update the roles mapping. this is like pressing
#    the button 'Update Security Setting' and portal_workflow"""
#    if isNotdublettefinderProfile(context): return
#    shortContext = context._profile_path.split(os.path.sep)[-3]
#    if shortContext != 'dublettefinder': # avoid infinite recursions
#        return
#    wft = getToolByName(context.getSite(), 'portal_workflow')
#    wft.updateRoleMappings()

def postInstall(context):
    """Called as at the end of the setup process. """
    # the right place for your custom code
    if isNotdublettefinderProfile(context): return
    shortContext = context._profile_path.split(os.path.sep)[-3]
    if shortContext != 'dublettefinder': # avoid infinite recursions
        return
    site = context.getSite()
    register_config_settings(site)



##code-section FOOT
def register_config_settings(portal):
    sm = portal.getSiteManager()
    if not sm.queryUtility(IDubletteFinderConfiguration,
                           name='dublettefinder_config'):

        sm.registerUtility(DubletteFinderConfiguration(),
                           IDubletteFinderConfiguration,
                           'dublettefinder_config')
##/code-section FOOT
