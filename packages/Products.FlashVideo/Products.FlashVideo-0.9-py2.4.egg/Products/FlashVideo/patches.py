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

# Python
import mimetypes
from logging import getLogger
# Plone
from Products.CMFPlone import utils
from Products.CMFCore.PortalFolder import PortalFolderBase
# Flash Video
from Products.FlashVideo.config import FLASHVIDEO_PORTALTYPE
from Products.FlashVideo.config import PROJECTNAME
from Products.FlashVideo.config import FLASHVIDEO_MIMETYPE
    
log = getLogger(PROJECTNAME)

# '_createObjectByType' is used by PloneFlashUpload
# Patch this method to remove dots in object id.
# If url ends with .flv uploaded image screenshot will not be 
# displayed. This is something wrong with FlowPlayer
old_createObjectByType = utils._createObjectByType
def new_createObjectByType(type_name, container, id, *args, **kw):
    """
    Prevent ids from having dots inside for Flash Video objects.
    Flow Player doesn't like that.
    """    
    if type_name == FLASHVIDEO_PORTALTYPE:
        id = id.replace(".","_")
    return old_createObjectByType(type_name, container, id, *args, **kw)
    
log.info("Applying patch for Products.CMFPlone.utils._createObjectByType")
utils._createObjectByType = new_createObjectByType

# Load additional file types to mimetypes module
# Necessary for FTP/WebDAV to work
mimetypes.add_type("video/x-flv",".flv")
