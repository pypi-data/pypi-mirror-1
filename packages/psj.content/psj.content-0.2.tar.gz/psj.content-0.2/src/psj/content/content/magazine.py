##
## magazine.py
## Login : <uli@pu.smp.net>
## Started on  Wed Jun  4 00:15:50 2008 Uli Fouquet
## $Id$
## 
## Copyright (C) 2008 Uli Fouquet
## This program is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 2 of the License, or
## (at your option) any later version.
## 
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
## 
## You should have received a copy of the GNU General Public License
## along with this program; if not, write to the Free Software
## Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
##
"""
An Magazine or series.
"""
from zope.interface import implements
from Products.Archetypes import atapi
from Products.ATContentTypes.content import folder
from Products.ATContentTypes.content.schemata import finalizeATCTSchema

from psj.content.interfaces import IMagazine
from psj.content.config import PROJECTNAME
from psj.content import PSJContentMessageFactory as _


PSJMagazineSchema = folder.ATFolderSchema.copy()

PSJMagazineSchema['title'].storage = atapi.AnnotationStorage()
PSJMagazineSchema['description'].storage = atapi.AnnotationStorage()

finalizeATCTSchema(PSJMagazineSchema, folderish=True, moveDiscussion=False)

class PSJMagazine(folder.ATFolder):
    implements(IMagazine)

    portal_type = 'PSJMagazine'
    _at_rename_after_creation = True
    schema = PSJMagazineSchema
    annotations_key = 'psj.content'

    def rebuild(self):
        pass

atapi.registerType(PSJMagazine, PROJECTNAME)

