##
## fields.py
## Login : <uli@pu.smp.net>
## Started on  Mon May 26 02:08:35 2008 Uli Fouquet
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
Fields for extended schemata.
"""
from Products.Archetypes.public import (BooleanField, TextField, LinesField,
                                        ReferenceField,)
from archetypes.schemaextender.field import ExtensionField

class PSJBooleanField(ExtensionField, BooleanField):
    """A boolean field."""

class PSJTextLineField(ExtensionField, TextField):
    """A text line field."""

class PSJTextField(ExtensionField, PSJTextLineField):
    """A text field."""

class PSJRelationField(ExtensionField, ReferenceField):
    """A relation field."""
    
class PSJLinesField(ExtensionField, LinesField):
    """A lines field."""
