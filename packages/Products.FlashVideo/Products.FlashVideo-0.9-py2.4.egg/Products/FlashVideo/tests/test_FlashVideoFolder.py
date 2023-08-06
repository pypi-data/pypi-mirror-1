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
Unit tests for FlashVideoFolder class
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

VIDEO_FOLDER_ID = 'videofolder'
    
class FlashVideoFolderUnitTests(PloneUnitTestCase):
    """
    Test class for FlashVideoFolder class.  
    """        
    portal_type = FLASHVIDEOFOLDER_PORTALTYPE
    object_id = VIDEO_FOLDER_ID
      
class FlashVideoFolderIntegrationTestCase(PloneIntegrationTestCase):
    """
    Functional tests checking that all configuation works
    """
    portal_type = FLASHVIDEOFOLDER_PORTALTYPE
    object_id = VIDEO_FOLDER_ID
    type_properties = (('immediate_view','flashvideofolder_view'),
                       ('default_view','flashvideofolder_view'),
                       ('content_icon','flashvideofolder_icon.gif'),
                       ('allowed_content_types',(FLASHVIDEO_PORTALTYPE,
                                                 FLASHVIDEOPLAYLIST_PORTALTYPE)),
                       ('global_allow',True),
                       ('filter_content_types',True),
                       )
    skin_files = ('flashvideofolder_icon.gif',
                  'flashvideofolder_view', )
    object_actions = ['view', 'edit', 'metadata', 'local_roles', 'folderContents']
    
class FlashVideoFolderFunctionalTestCase(PloneFunctionalTestCase):
    """
    Functional tests for view and edit templates
    """
    portal_type = FLASHVIDEOFOLDER_PORTALTYPE
    object_id = VIDEO_FOLDER_ID
        
        
def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(FlashVideoFolderUnitTests))
    suite.addTest(makeSuite(FlashVideoFolderFunctionalTestCase))
    suite.addTest(makeSuite(FlashVideoFolderIntegrationTestCase))
    
    return suite

if __name__ == '__main__':
    framework()


