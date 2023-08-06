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

#Zope
from AccessControl import ClassSecurityInfo
from Products.CMFCore.permissions import View
from Products.ATContentTypes.content.folder import ATFolder
from Products.ATContentTypes.content.folder import ATFolderSchema
from Products.ATContentTypes.content.schemata import finalizeATCTSchema
#Try multilingual support
#try:
    #from Products.LinguaPlone.public import *
#except ImportError: 
from Products.Archetypes.public import *

#Product
from Products.FlashVideo.config import *

FlashVideoFolderSchema = ATFolderSchema.copy()

class FlashVideoFolder(ATFolder):    
    schema                = FlashVideoFolderSchema
    content_icon          = 'flashvideofolder_icon.gif'
    meta_type             = FLASHVIDEOFOLDER_METATYPE
    portal_type           = FLASHVIDEOFOLDER_PORTALTYPE
    archetype_name        = FLASHVIDEOFOLDER_PORTALTYPE
    allowed_content_types = ()
    filter_content_types  = 1
    immediate_view        = 'flashvideofolder_view'
    default_view          = 'flashvideofolder_view'
    filter_content_types  = 1
    allowed_content_types = (FLASHVIDEO_PORTALTYPE,FLASHVIDEOPLAYLIST_PORTALTYPE,)
    typeDescription       = 'A folder which contains Flash video (*.flv) files and playlists.'
    typeDescMsgId         = 'description_type_flashvideofolder'
    
    __implements__ = ATFolder.__implements__
    security       = ClassSecurityInfo()
        
registerType(FlashVideoFolder,PROJECTNAME)
