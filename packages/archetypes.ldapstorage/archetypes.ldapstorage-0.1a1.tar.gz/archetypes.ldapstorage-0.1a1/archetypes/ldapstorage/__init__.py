#  -*- coding: utf8 -*-
#  Copyright (c) 2007 Eurotux Informática S.A.
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
"""
An Archetypes storage that stores the field values in an LDAP directory.
"""

__author__  = 'Ricardo Alves <rsa at eurotux dot com>'
__docformat__ = 'plaintext'

from storage import LDAPStorage
import config
from Products.CMFCore import utils as cmfutils
from Products.Archetypes import public as atapi
from Products.CMFCore import permissions

def initialize(context):

    #if config.DEBUG_MODE:
    import examples.ExampleContent
    import examples.ExampleContent2

    project_name = config.PROJECT_NAME

    # Process the project's types
    content_types, constructors, ftis = \
        atapi.process_types(atapi.listTypes(project_name), project_name)

    cmfutils.ContentInit(
        meta_type           = project_name + ' Content',
        content_types       = content_types,
        permission          = permissions.AddPortalContent,
        extra_constructors  = constructors,
        fti                 = ftis,
    ).initialize(context)
