#  FlashVideo http://plone.org/products/flashvideo
#  Simple solutions for online videos for Plone
#  Copyright (c) 2008-2009 Lukasz Lakomy
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

from Products.Archetypes.public import process_types
from Products.Archetypes import listTypes
from Products.CMFCore.utils import ContentInit
from Products.CMFCore.DirectoryView import registerDirectory
from Products.CMFCore.permissions import AddPortalContent
from Products.validation import validation

#Product
from validators import FLVValidator 
validation.register(FLVValidator('isFLVFile'))

from config import *
from content import FlashVideo
from content import FlashVideoFolder
from content import FlashVideoPlaylist

import patches

registerDirectory(SKINS_DIR, GLOBALS)

def initialize(context):
    
    # initialize portal content
    all_content_types, all_constructors, all_ftis = process_types(
        listTypes(PROJECTNAME),
        PROJECTNAME)
        
    ContentInit(
        PROJECTNAME + ' Content',
        content_types      = all_content_types,
        permission         = AddPortalContent,
        extra_constructors = all_constructors,
        fti                = all_ftis,
        ).initialize(context)

try:
    from Products.GenericSetup.tool import SetupTool
    from Products.GenericSetup import profile_registry
    from Products.GenericSetup import BASE, EXTENSION
    profile_registry.registerProfile('default',
                                     'FlashVideo',
                                     'Extension profile for FlashVideo',
                                     'profiles/default',
                                     'FlashVideo',
                                     EXTENSION)
except:
    #Plone < 2.5
    pass
    
