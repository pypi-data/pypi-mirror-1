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
from webdav.common import rfc1123_date
#import transaction
from AccessControl import ClassSecurityInfo
from Products.CMFCore.permissions import View
from Products.CMFCore.permissions import ModifyPortalContent
from Products.ATContentTypes.content.base import ATCTContent
from Products.ATContentTypes.content.schemata import ATContentTypeSchema
from Products.ATContentTypes.content.schemata import finalizeATCTSchema
from Products.ATReferenceBrowserWidget.ATReferenceBrowserWidget import ReferenceBrowserWidget

#Try multilingual support
#try:
    #from Products.LinguaPlone.public import *
#except ImportError: 
from Products.Archetypes.public import *

#Product
from Products.FlashVideo.config import *
from Products.FlashVideo.utils import updateActions

FlashVideoPlaylistSchema = ATContentTypeSchema.copy() + Schema((
    
     ReferenceField('videos',
                    relationship = 'videos',
                    multiValued = True,
                    required=0,
                    allowed_types=(FLASHVIDEO_PORTALTYPE,),
                    widget = ReferenceBrowserWidget(
                        label = "Videos in playlist",
                        description = "Select videos to display inside this playlist",
                        label_msgid = "label_video_playlist",
                        description_msgid = "help_video_playlist",                        
                        i18n_domain = "plone",),
                    ),
    
    ),marshall=PrimaryFieldMarshaller()
    )

finalizeATCTSchema(FlashVideoPlaylistSchema)

class FlashVideoPlaylist(ATCTContent):    
    schema                = FlashVideoPlaylistSchema
    content_icon          = 'flashvideoplaylist_icon.gif'
    meta_type             = FLASHVIDEOPLAYLIST_METATYPE
    portal_type           = FLASHVIDEOPLAYLIST_PORTALTYPE
    archetype_name        = FLASHVIDEOPLAYLIST_PORTALTYPE
    allowed_content_types = ()
    filter_content_types  = False
    immediate_view        = 'flashvideoplaylist_view'
    default_view          = 'flashvideoplaylist_view'
    typeDescription       = 'Playlist allows viewing multiple Flash videos in a row.'
    typeDescMsgId         = 'description_type_flashvideoplaylist'
    _at_rename_after_creation = True
    
    __implements__ = ATCTContent.__implements__
    security       = ClassSecurityInfo()
        
    actions = updateActions(ATCTContent,(
        {'id'          : 'play',
         'name'        : 'Play',
         'action'      : 'string:${object_url}/flashvideoplaylist_play',
         'permissions' : (View,)},
        )
    )
    
    security.declareProtected(View,'screenshot_mini')
    def screenshot_mini(self, REQUEST=None, RESPONSE=None):
        """
        Use similar approach for displaying thumbnails in folder listing 
        like in Flash Video to use the same link in templates.
        """
        videos = self.getVideosList()
        image = None
        if videos:
            video = videos[0]
            field = video.getField('screenshot')
            sizes = field.getAvailableSizes(video).keys()
            if 'mini' in sizes:
                image = field.getScale(video, scale='mini')
            if image is not None and not isinstance(image, basestring):
                # image might be None or '' for empty images
                if RESPONSE:
                    RESPONSE.setHeader('Last-Modified', rfc1123_date(image._p_mtime))
                    RESPONSE.setHeader('Content-Type', image.content_type)
                    RESPONSE.setHeader('Content-Length', image.size)
                    RESPONSE.setHeader('Accept-Ranges', 'bytes')
                return image.data
        return None
    
    security.declareProtected(View,'getVideosList')
    def getVideosList(self):
        """
        """
        result = []
        result = self.getVideos()
        return result
    
    def getPlaylistWidth(self):
        """
        Playlist width (resolution) is the same as width of first movie
        """
        videos = self.getVideosList()
        if videos:
            result = videos[0].getMovieWidth()
        else:
            result = DEFAULT_VIDEO_WIDTH
        return result
        
    def getPlaylistHeight(self):
        """
        Playlist height (resolution) is the same as height of first movie
        """
        videos = self.getVideosList()
        if videos:
            result = videos[0].getMovieHeight()
        else:
            result = DEFAULT_VIDEO_HEIGHT
        return result
        
    def getPlaylistUrls(self):
        """
        Get absolute urls of all movies in list
        """
        videos = self.getVideosList()
        result = []
        for video in videos:
            result.append(video.absolute_url())
        return result
        
    def getPlaylistString(self):
        """
        Create string required for javascript function to display
        all movies in playlist
        """
        urls = self.getPlaylistUrls()
        result = ""
        for url in urls:
            result += "{url: \'%s\', type: \'flv\'},"%(url)
        return result
    
    def getPlaylistScreenshot(self):
        """
        Get image of first movie as a playlist screenshot
        """
        videos = self.getVideosList()
        if videos:
            result = "%s/screenshot"%(videos[0].absolute_url())
        else:
            result = ""
        return result
    
registerType(FlashVideoPlaylist,PROJECTNAME)
