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

from zope.interface import Interface
from plone.indexer.decorator import indexer

@indexer(Interface)
def getFileNames(obj, **kwargs):
    fields = obj.Schema().fields()
    names = [f.get(obj).filename for f in fields if f.type in ['file', 'blob', 'image']]
    return names

@indexer(Interface)
def getFileSizes(obj, **kwargs):
    fields = obj.Schema().fields()
    sizes = [f.get(obj).get_size() for f in fields if f.type in ['file', 'blob', 'image']]
    return sizes

