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

"""Unit tests for FlashVideo class"""

import os
import sys
import types
import mimetypes

if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py')) 

# Zope
from Acquisition import aq_base
import transaction

# CMF
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import utils

# FlashVideo
from Products.FlashVideo.content.FlashVideo import FlashVideo
from Products.FlashVideo.config import *
from Products.FlashVideo.FLVHeader import FLVHeaderError

from Products.FlashVideo.tests.utils import getRequest
from Products.FlashVideo.tests.BaseTest import PloneFunctionalTestCase
from Products.FlashVideo.tests.BaseTest import PloneIntegrationTestCase
from Products.FlashVideo.tests.BaseTest import PloneUnitTestCase

VIDEO_ID = 'video'
    
class FlashVideoUnitTests(PloneUnitTestCase):
    """Test class for FlashVideo class. Things that need to be 
    tested:
     - changing object id (from title not from file)
     - setting attributes (mainly file and image)
     - resolution ofter uploading a file
     - access to 'screenshot' image
     - access to different screenshot scales
     - getting movie width and height (from image resolution)    
    """        
    portal_type = FLASHVIDEO_PORTALTYPE
    object_id = VIDEO_ID
    
    def test___bobo_traverse__(self):
        """Test tricks to have access to image field accessible as
        'screenshot' URL
        """
        video = self.createInstance()
        
        request = getRequest()
        image = self.getImageFile()
        video.setScreenshot(image)
        obj = video.__bobo_traverse__(request,'screenshot')
        self.assertNotEqual(obj,None)
        obj = video.__bobo_traverse__(request,'screenshot_mini')
        self.assertNotEqual(obj,None)
        
    def test_setATCTFileContent(self):
        """Test overriden method that should contstruct a valid id
        from title instead of making one from file name
        """
        video = self.createInstance()
        movie = self.getMovieFile()

        empty = video.getFile()
        #print "type(empty)",type(empty)
        if type(empty) == types.StringType:
            #Plone 2.5, 3.1 returns empty string
            self.assertEqual(empty,'')
        else:
            #Plone 2.1, 3.0 have empty File object
            self.assertEqual(empty.get_size(),0)
        video._setATCTFileContent(movie)       
        self.assertNotEqual(video.getFile(),'')
        self.assertEqual(video.getId(),self.object_id)
        self.assertNotEqual(video.getId(),movie.filename)

    def test_setWidth(self):
        """Simple test for setting width"""
        video = self.createInstance()        
        self.assertNotEqual(video.getWidth(),333)
        video.setWidth(333)
        self.assertEqual(video.getWidth(),333)
        
    def test_setHeight(self):
        """Simple test for setting height"""
        video = self.createInstance()        
        self.assertNotEqual(video.getHeight(),333)
        video.setHeight(333)
        self.assertEqual(video.getHeight(),333)
        
    def test_setFile(self):
        """Check method that sets file. Check if width and heigh are
        set correctly
        """
        video = self.createInstance()
        movie = self.getMovieFile()
                    
        empty = video.getFile()
        #print "type(empty)",type(empty)
        if type(empty) == types.StringType:
            #Plone 2.5, 3.1 returns empty string
            self.assertEqual(empty,'')
        else:
            #Plone 2.1, 3.0 have empty File object
            self.assertEqual(empty.get_size(),0)
            
        self.assertEqual(video.getWidth(),'')
        self.assertEqual(video.getHeight(),'')
        
        video.setFile(movie)
        self.assertEqual(video.getWidth(),130)
        self.assertEqual(video.getHeight(),70)
        
        file_ = video.getFile()
        # This is weird, why size is 0 after uploading file?
        self.assertNotEqual(file_,'')
        self.assertNotEqual(file_.get_size(),0)
        self.assertNotEqual(file_.getContentType(),FLASHVIDEO_MIMETYPE)
       
    def test_setFile_bad(self):
        """Check if error is raised when uploading wrong file"""
        video = self.createInstance()
        image = self.getImageFile()        
        self.assertRaises(FLVHeaderError,video.setFile,image)               
        
    def test_getMovieWidthHeight1(self):
        """Check if width of video is set according to resolution of screenshot."""
        video = self.createInstance()
        movie = self.getMovieFile()
        image = self.getImageFile()
        
        self.assertEqual(video.getMovieWidth(),DEFAULT_VIDEO_WIDTH)
        self.assertEqual(video.getMovieHeight(),DEFAULT_VIDEO_HEIGHT)
        video.setScreenshot(image)
        self.assertEqual(video.getMovieWidth(),130)
        self.assertEqual(video.getMovieHeight(),70)
        
    def test_getMovieWidthHeight2(self):
        """Check if width of video is set according to resolution of movie."""
        video = self.createInstance()
        movie = self.getMovieFile()
        image = self.getImageFile()
        
        self.assertEqual(video.getMovieWidth(),DEFAULT_VIDEO_WIDTH)
        self.assertEqual(video.getMovieHeight(),DEFAULT_VIDEO_HEIGHT)
        video.setFile(movie)
        self.assertEqual(video.getMovieWidth(),130)
        self.assertEqual(video.getMovieHeight(),70)
        
    def test_createObject(self):
        """Test creation of simple class instance"""
        self.createInstance()
        ids = self.folder.objectIds()
        self.assertEqual(self.object_id in ids, True)
        movie = self.folder._getOb(self.object_id)
        self.assertEqual(movie.portal_type, FLASHVIDEO_PORTALTYPE)
        self.assertEqual(movie.getId(), self.object_id)

    def test_getId(self):
        """Check if object id is changed after upload"""
        fakefile = self.getMovieFile()
        id = self.folder.invokeFactory(self.portal_type,
                                       id = self.object_id,
                                       file=fakefile)        
        self.assertEqual(id, self.object_id)
        obj = self.folder._getOb(id)
        self.assertEqual(obj.getId(), self.object_id)
        self.assertNotEqual(obj.getId(),fakefile.filename)
    
    def test_hasScreenshot(self):
        """Setting up screenshot and checking if exists"""
        video = self.createInstance()        
        movie = self.getMovieFile()
        image = self.getImageFile()
        
        video.setFile(movie)
        self.assertEqual(video.hasScreenshot(),False)
        
        video.setScreenshot(image)
        self.assertEqual(video.hasScreenshot(),True)
             
    def test_getConfigString(self):
        """Test if configuration code in javascript changes
        when screenshot is defined.
        """
        video = self.createInstance()        
        movie = self.getMovieFile()
        image = self.getImageFile()
        
        video.setFile(movie)
        conf = video.getConfigString()
        self.assertEqual(conf.find("/screenshot'")>=0, False)
        
        video.setScreenshot(image)
        conf = video.getConfigString()
        self.assertEqual(conf.find("/screenshot'")>=0, True)
                   
class FlashVideoIntegrationTestCase(PloneIntegrationTestCase):
    """Functional tests checking that all configuation works"""
    
    portal_type = FLASHVIDEO_PORTALTYPE
    object_id = VIDEO_ID
    type_properties = (('immediate_view','flashvideo_view'),
                       ('default_view','flashvideo_view'),
                       ('content_icon','flashvideo_icon.gif'),
                       ('allowed_content_types',()),
                       ('global_allow',True),
                       ('filter_content_types',False),
                       )
    skin_files = ('FlowPlayerDark.swf',
                  'flashvideo_icon.gif',
                  'flashvideo_view',
                  'swfobject.js' )
    
    def test_installation(self):
        """Test if installation script works, regardless of
        use of portal_setup or portal_quickinstaller.
         - check if contet_type_registry updated
         - check if mimetypes_registry updated 
        """
        content_type_registry = getToolByName(self.portal,'content_type_registry')
        mimetypes_registry = getToolByName(self.portal,'mimetypes_registry')
        
        # Content type registry
        predicate_ids = content_type_registry.predicate_ids
        # New predicates added
        self.assertEqual('flv' in predicate_ids, True)
        self.assertEqual('video/x-flv' in predicate_ids, True)
        # Old video predicate moved to the bottom
        self.assertEqual(predicate_ids[-1], 'video')

        # Mime types registry
        mimetypes = mimetypes_registry.lookup('video/x-flv')
        self.assertEqual(len(mimetypes), 1) 
        self.assertEqual(mimetypes[0].extensions, ['flv'])
        self.assertEqual(mimetypes[0].icon_path, 'flashvideo_icon.gif')
               
    def test_mimetypes(self):
        """Check if new mimetype x-flv is added during startup"""
        ext = mimetypes.guess_extension(FLASHVIDEO_MIMETYPE)
        self.assertEqual(ext, ".%s"%FLASHVIDEO_FILE_EXT)
        typ, encoding = mimetypes.guess_type(".%s"%FLASHVIDEO_FILE_EXT)
        self.assertEqual(typ, FLASHVIDEO_MIMETYPE)               
        
class FlashVideoFunctionalTestCase(PloneFunctionalTestCase):
    """Functional tests for view and edit templates"""
    
    portal_type = FLASHVIDEO_PORTALTYPE
    object_id = VIDEO_ID
        
    def test_createObjectViaWebDAV(self):
        """Check if upload via WebDAV/FTP works:
         - file is created
         - dots and .flv suffix is removed
         - title is set
        """        
        # Patch method called after file is uploaded to avoid CopyError
        def new_manage_afterPUT(self, data, marshall_data, file, context, mimetype,
                                filename, REQUEST, RESPONSE):
            transaction.commit()
            self.old_manage_afterPUT(data, marshall_data, file, context, mimetype,
                                     filename, REQUEST, RESPONSE)
        FlashVideo.old_manage_afterPUT = FlashVideo.manage_afterPUT
        FlashVideo.manage_afterPUT = new_manage_afterPUT
            
        self.failIf('test_movie' in self.folder.objectIds())
        movie_file = self.getMovieFile()
        response = self.publish(self.folder_path+'/test_movie.flv', request_method='PUT',
                                stdin=movie_file, basic=self.basic_auth)
        self.assertEqual(response.getStatus(), 201)
        # Id should be changed
        self.failUnless('test_movie' in self.folder.objectIds())
        movie = self.folder.test_movie
        # Meta type must be correct (from content_registry)
        self.assertEqual(movie.portal_type, FLASHVIDEO_PORTALTYPE)
        # Title generated from id
        self.assertEqual(movie.Title(), "Test movie")
        self.assertEqual(movie.getContentType(),FLASHVIDEO_MIMETYPE)
        
    def test_createObjectByType(self):
        """Test patched method, that is used for example in
        PloneFlashUpload
        """
        obj = utils._createObjectByType(FLASHVIDEO_PORTALTYPE, self.folder, VIDEO_ID)
        self.assertEqual(VIDEO_ID in self.folder.objectIds(),True)
        movie = getattr(self.folder,VIDEO_ID)
        self.assertEqual(movie.portal_type, FLASHVIDEO_PORTALTYPE)        
        
    def test_fileStorage(self):
        """If FSS is installed stored video is an instance of FSS class.
        If not it is stored as OFS.Image
        """      
        portal_quickinstaller = getToolByName(self.portal,'portal_quickinstaller')
        movie_file = self.getMovieFile()
        self.folder.invokeFactory(self.portal_type, id=self.object_id) 
        movie = self.folder._getOb(self.object_id)
        movie.setFile(movie_file)        
        
        # Size
        file_ = movie.getFile()
        if portal_quickinstaller.isProductInstalled("FileSystemStorage"):
            from Products.FileSystemStorage.FileSystemStorage import VirtualFile as FileClass
        else:
            from OFS.Image import File as FileClass
        self.assertEqual(isinstance(file_,FileClass),True)
        
        
def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(FlashVideoUnitTests))
    suite.addTest(makeSuite(FlashVideoFunctionalTestCase))
    suite.addTest(makeSuite(FlashVideoIntegrationTestCase))
    
    return suite

if __name__ == '__main__':
    framework()


