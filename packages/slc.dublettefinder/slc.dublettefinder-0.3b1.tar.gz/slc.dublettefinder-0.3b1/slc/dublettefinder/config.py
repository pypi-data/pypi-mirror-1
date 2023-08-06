# -*- coding: utf-8 -*-
# Copyright (c) 2008 by Syslab.com GmbH
# GNU General Public License (GPL)

__author__ = """JC Brand <brand@syslab.com>"""
__docformat__ = 'plaintext'

from OFS.SimpleItem import SimpleItem

from zope.component import getUtility
from zope.interface import implements
from zope.schema.fieldproperty import FieldProperty

from Products.CMFCore.permissions import setDefaultRoles

from interfaces import IDubletteFinderConfiguration

PROJECTNAME = "dublettefinder"

# Permissions
DEFAULT_ADD_CONTENT_PERMISSION = "Add portal content"
setDefaultRoles(DEFAULT_ADD_CONTENT_PERMISSION, ('Manager', 'Owner'))

product_globals = globals()

DEPENDENCIES = []
PRODUCT_DEPENDENCIES = []

class DubletteFinderConfiguration(SimpleItem):
    implements(IDubletteFinderConfiguration)
    check_file_size = \
        FieldProperty(IDubletteFinderConfiguration['check_file_size'])

    allowable_size_deviance = \
        FieldProperty(IDubletteFinderConfiguration['allowable_size_deviance'])
        
    check_file_name = \
        FieldProperty(IDubletteFinderConfiguration['check_file_name'])

    check_object_name = \
        FieldProperty(IDubletteFinderConfiguration['check_object_name'])


def form_adapter(context):
    return getUtility(IDubletteFinderConfiguration,
                      name='dublettefinder_config',
                      context=context)

try:
    from Products.dublettefinder.AppConfig import *
except ImportError:
    pass

