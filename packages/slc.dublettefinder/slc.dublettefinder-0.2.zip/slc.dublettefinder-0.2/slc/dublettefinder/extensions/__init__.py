# -*- coding: utf-8 -*-
#
# File: extensions.py
#
# Copyright (c) 2008 by Opkode CC
# Generator: ArchGenXML Version 2.0
#            http://plone.org/products/archgenxml
#
# GNU General Public License (GPL)
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301, USA.
#

__author__ = """JC Brand <jc@opkode.co.za>"""
__docformat__ = 'plaintext'


##code-section init-module-header #fill in your manual code here
from Products.CMFPlone.CatalogTool import _eioRegistry
##/code-section init-module-header


# Subpackages
# Additional

# Classes

##code-section init-module-footer #fill in your manual code here
def getFileNames(obj, portal, **kwargs):
    fields = obj.Schema().fields()
    names = [f.get(obj).filename for f in fields if f.type in ['file', 'blob', 'image']]
    return names

def getFileSizes(obj, portal, **kwargs):
    fields = obj.Schema().fields()
    sizes = [f.get(obj).get_size() for f in fields if f.type in ['file', 'blob', 'image']]
    return sizes

_eioRegistry.register('getFileSizes', getFileSizes)
_eioRegistry.register('getFileNames', getFileNames)
##/code-section init-module-footer

