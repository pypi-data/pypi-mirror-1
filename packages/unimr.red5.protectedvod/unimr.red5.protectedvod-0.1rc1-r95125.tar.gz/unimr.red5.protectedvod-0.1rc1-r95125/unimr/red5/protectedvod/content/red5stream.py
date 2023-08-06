#  Red5Stream http://www.uni-marburg.de/hrz
#  Protected streaming via plone & red5
#  Copyright (c) 2009 Andreas Gabriel <gabriel@hrz.uni-marburg.de>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
from zope.interface import implements

from AccessControl import ClassSecurityInfo
from Products.ATContentTypes.content.file import ATFile
from Products.ATContentTypes.content.file import ATFileSchema
from Products.ATContentTypes.content.schemata import finalizeATCTSchema
from Products.ATContentTypes.content.base import registerATCT

from iw.fss.FileSystemStorage import FileSystemStorage

from unimr.red5.protectedvod.interface import IRed5Stream
from unimr.red5.protectedvod.permissions import DownloadRed5Stream
from unimr.red5.protectedvod.config import PROJECTNAME

Red5StreamSchema = ATFileSchema.copy()

file_field = Red5StreamSchema['file']
file_field.storage = FileSystemStorage()
file_field.registerLayer('storage', file_field.storage)
file_field.read_permission = DownloadRed5Stream

finalizeATCTSchema(Red5StreamSchema)

class Red5Stream(ATFile):

    implements(IRed5Stream)
    portal_type    = 'Red5Stream'
    archetype_name = 'Red5Stream'
    inlineMimetypes= tuple()

    schema = Red5StreamSchema

    security       = ClassSecurityInfo()


    security.declareProtected(DownloadRed5Stream, 'index_html')
    security.declareProtected(DownloadRed5Stream, 'download')

registerATCT(Red5Stream, PROJECTNAME)
    
