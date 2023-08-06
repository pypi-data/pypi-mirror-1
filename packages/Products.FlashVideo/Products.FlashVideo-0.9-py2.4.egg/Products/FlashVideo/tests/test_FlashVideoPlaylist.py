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

"""
Unit tests for FlashVideoPlaylist class
"""
import os
import sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py')) 

from Products.FlashVideo.config import *
from Products.FlashVideo.tests.utils import getRequest

from BaseTest import PloneFunctionalTestCase
from BaseTest import PloneIntegrationTestCase
from BaseTest import PloneUnitTestCase

VIDEO_PLAYLIST_ID = 'videoplaylist'
VIDEO_ID1 = 'video1'

class FlashVideoPlaylistUnitTests(PloneUnitTestCase):
    """
    Test class for FlashVideoPlaylist class.  
    """        
    portal_type = FLASHVIDEOPLAYLIST_PORTALTYPE
    object_id = VIDEO_PLAYLIST_ID
      
    def createInstance(self):
        """
        Create object instance of defined portal_type
        """
        image = self.getImageFile()
        movie = self.getMovieFile()
        
        #Add movie
        self.folder.invokeFactory(FLASHVIDEO_PORTALTYPE,id=VIDEO_ID1)
        video = self.folder._getOb(VIDEO_ID1)
        video.setScreenshot(image)
        video.setFile(movie)
        #Create playlist
        self.folder.invokeFactory(self.portal_type, id=self.object_id)         
        playlist = self.folder._getOb(self.object_id)
        playlist.setVideos(video.UID())
        return playlist
    
    def test_createInstance(self):
        """
        Check if createInstance creates playlist with one 
        video file inside
        """
        playlist = self.createInstance()
        self.assertEqual(playlist.portal_type, self.portal_type)
        uids = playlist.getRawVideos()
        self.assertEqual(len(uids),1)
        video = self.folder._getOb(VIDEO_ID1)
        self.assertEqual(uids[0],video.UID())
        
    def test_getVideosList(self):
        """
        Get list of videos
        """
        playlist = self.createInstance()
        vl = playlist.getVideosList()
        self.assertEqual(len(vl),1)
        self.assertEqual(vl[0].getId(),VIDEO_ID1)
        
    def test_getPlaylistWidth(self):
        """
        Test if playlist width (resolution) is the same as width of first movie
        """
        playlist = self.createInstance()
        self.assertEqual(playlist.getPlaylistWidth(),130)#70
        
    def test_getPlaylistHeight(self):
        """
        Test if playlist height (resolution) is the same as height of first movie
        """
        playlist = self.createInstance()
        self.assertEqual(playlist.getPlaylistHeight(),70)
        
    def test_getPlaylistUrls(self):
        """
        Get absolute urls of all movies in list
        """
        playlist = self.createInstance()
        urls = playlist.getPlaylistUrls()
        self.assertEqual(len(urls),1)
        self.assertEqual(urls[0].endswith(VIDEO_ID1),True)
        
    def test_getPlaylistString(self):
        """
        Check generated string for javascript if contains one
        video url
        """
        playlist = self.createInstance()
        url = self.folder._getOb(VIDEO_ID1).absolute_url()
        self.assertEqual(playlist.getPlaylistString(),
                         "{url: \'%s\', type: \'flv\'},"%(url))
        
    def test_getPlaylistScreenshot(self):
        """
        Check if playlist screenshot url is the same as video url
        """
        playlist = self.createInstance()
        screenshot = playlist.getPlaylistScreenshot()
        url = self.folder._getOb(VIDEO_ID1).absolute_url()
        self.assertEqual(screenshot,"%s/screenshot"%(url))      
    
    def test_screenshot_mini(self):
        """
        Check method for displaying screenshot_mini. Check with REQUEST
        and without.
        """
        playlist = self.createInstance()
        mini = playlist.screenshot_mini()
        self.assertNotEqual(mini,None)
        self.assertEqual(len(mini),3159)
        #with request
        response = getRequest().RESPONSE        
        content_type = response.getHeader('content-type')
        self.assertEqual(content_type,None)
        mini2 = playlist.screenshot_mini(RESPONSE=response)
        self.assertNotEqual(mini,None)
        self.assertEqual(len(mini),3159)
        content_type = response.getHeader('content-type')
        self.assertEqual(content_type,'image/jpeg')
    
class FlashVideoPlaylistIntegrationTestCase(PloneIntegrationTestCase):
    """
    Functional tests checking that all configuation works
    """
    portal_type = FLASHVIDEOPLAYLIST_PORTALTYPE
    object_id = VIDEO_PLAYLIST_ID
    type_properties = (('immediate_view','flashvideoplaylist_view'),
                       ('default_view','flashvideoplaylist_view'),
                       ('content_icon','flashvideoplaylist_icon.gif'),
                       ('allowed_content_types',()),
                       ('global_allow',True),
                       ('filter_content_types',False),
                       )
    skin_files = ('flashvideoplaylist_icon.gif',
                  'flashvideoplaylist_view', )
    object_actions = ['view', 'edit', 'metadata', 'local_roles', 'play']
    type_actions = ['view', 'edit', 'metadata', 'local_roles', 'play']
    
class FlashVideoPlaylistFunctionalTestCase(PloneFunctionalTestCase):
    """
    Functional tests for view and edit templates
    """
    portal_type = FLASHVIDEOPLAYLIST_PORTALTYPE
    object_id = VIDEO_PLAYLIST_ID
           
def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(FlashVideoPlaylistUnitTests))
    suite.addTest(makeSuite(FlashVideoPlaylistFunctionalTestCase))
    suite.addTest(makeSuite(FlashVideoPlaylistIntegrationTestCase))
    
    return suite

if __name__ == '__main__':
    framework()


