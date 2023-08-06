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
Unit tests for FlashVideo
"""
import unittest
import sys
import os
from StringIO import StringIO

from Testing import ZopeTestCase
from Products.PloneTestCase import PloneTestCase
from Products.PloneTestCase.setup import default_user
from Products.PloneTestCase.setup import default_password
from Products.PloneTestCase.setup import portal_owner

from Products.CMFCore.utils import getToolByName
from Products.FlashVideo.content.FlashVideo import FlashVideo
from Products.FlashVideo.utils import IS_PLONE_21
from Products.FlashVideo.utils import IS_PLONE_30
from Products.FlashVideo.utils import IS_PLONE_31

import warnings
warnings.simplefilter("ignore")

products = []
try:
    #Can work without FSS but if exist must be added and installed 
    #Otherwise there will be errors during tests
    from Products.FileSystemStorage import config
    ZopeTestCase.installProduct('FileSystemStorage')
    products.append('FileSystemStorage')
except ImportError:
    pass
products.append('FlashVideo')
ZopeTestCase.installProduct('FlashVideo')
PloneTestCase.setupPloneSite(products=products)

class FakeFile(StringIO):
    filename = 'fake_file'
    
class PloneUnitTestCase(PloneTestCase.PloneTestCase): 
    
    portal_type = ''
    object_id = ''
    
    def getMovieFile(self):
        """
        Get test flash video file
        """
        ihome = os.environ.get('INSTANCE_HOME')
        path = os.path.join(ihome,"Products","FlashVideo","tests","test_movie.flv")
        data = file(path,"r").read()
        fakefile = FakeFile()    
        fakefile.write(data)
        return fakefile
    
    def getImageFile(self):
        """
        Get teswt image file
        """
        ihome = os.environ.get('INSTANCE_HOME')
        path = os.path.join(ihome,"Products","FlashVideo","tests","test_movie.jpg")
        f = file(path,"rb")
        data = f.read()
        fakefile = FakeFile()    
        fakefile.write(data)
        f.close()
        return fakefile

    def createInstance(self):
        """
        Create object instance of defined portal_type
        """
        self.folder.invokeFactory(self.portal_type, id=self.object_id) 
        obj = self.folder._getOb(self.object_id)
        return obj
      
class PloneIntegrationTestCase(PloneTestCase.PloneTestCase):
    """
    Functional tests checking that all configuration works
    """
    portal_type = ''
    object_id = ''
    type_properties = (('',''),)
    skin_files = ()
    object_actions = ['view', 'edit', 'metadata', 'local_roles']
    type_actions = ['view', 'edit', 'metadata', 'local_roles']
    
    def afterSetUp(self):
        """
        Run before tests
        """
        if IS_PLONE_21:
            if 'references' not in self.type_actions:
                self.type_actions.append('references')
        if IS_PLONE_30 or IS_PLONE_31:
            if 'local_roles' in self.type_actions:
                self.type_actions.remove('local_roles')
                
    def test_object_actions(self):
        """
        Test if object have all required tabs
        """
        id = self.folder.invokeFactory(self.portal_type,
                                       id = self.object_id)        
        obj = self.folder._getOb(id)
        portal_actions = getToolByName(self.folder, 'portal_actions')
        actions = portal_actions.listFilteredActionsFor(obj)
        object_actions = actions['object']
        object_actions_ids = [x['id'] for x in object_actions]
        #print "\n\ntest_object_actions",object_actions_ids,"\n\n"

        self.assertEqual(len(object_actions_ids),len(self.object_actions),
                         "%s object should have %d actions, has %d"%(
                             self.portal_type, len(self.object_actions), len(object_actions_ids),))
        for action in self.object_actions:
            self.failUnless(action in object_actions_ids,
                            "%s object should have '%s' action"%(self.portal_type,action))
        
    def test_portal_types(self):
        """
        Test type in portal_types
        """
        portal_types = getToolByName(self.folder, 'portal_types')
        self.failUnless(self.portal_type in portal_types.objectIds(),
                        "%s not found in portal_types"%self.portal_type)
        type = portal_types.getTypeInfo(self.portal_type)
        self.failUnless(type, "%s not found in portal_types"%self.portal_type)
        
    def test_portal_type_properties(self):
        """
        'Flash Video' portal type properties
        """        
        portal_types = getToolByName(self.folder, 'portal_types')
        type = portal_types.getTypeInfo(self.portal_type)
        #type properties
        for p in self.type_properties:
            p_val = getattr(type,p[0],None)
            self.assertEqual(p_val,p[1],
                             "'%s' type property '%s' set to '%s' instead of '%s'"%(
                                 self.portal_type,p[0],p_val,p[1]))
        
    def test_portal_type_actions(self):
        """
        Portal type actions
        """        
        portal_types = getToolByName(self.folder, 'portal_types')
        type = portal_types.getTypeInfo(self.portal_type)        
        #type actions
        type_actions = type.listActions()
        actions_ids = [x.getId() for x in type_actions if x.getVisibility()]
        #print "\ntype_actions_ids",actions_ids,"\n"
        self.assertEqual(len(actions_ids),len(self.type_actions),
                         "%s type should have %d actions, has %d"%(
                             self.portal_type, len(self.type_actions), len(actions_ids),))
        
        for action in self.type_actions:
            self.failUnless(action in actions_ids,
                            "%s type should have '%s' action"%(self.portal_type,action))
        
    def test_portal_skins(self):
        """
        Test if files exist in portal_skins
        """
        skin_name = 'FlashVideo'
        portal_skins = getToolByName(self.folder, 'portal_skins')
        self.failUnless(skin_name in portal_skins.objectIds())
        skin = getattr(portal_skins, skin_name)
        files = skin.objectIds()
        for f in self.skin_files:
            self.failUnless(f in files,
                            "%s object should have '%s' in skins"%(self.portal_type,f))
        
class PloneFunctionalTestCase(PloneTestCase.FunctionalTestCase):
    """
    Functional tests for view and edit templates
    """
    portal_type = ''
    object_id = ''
    
    def getMovieFile(self):
        """
        Get test flash video file
        """
        ihome = os.environ.get('INSTANCE_HOME')
        path = os.path.join(ihome,"Products","FlashVideo","tests","test_movie.flv")
        data = file(path,"r").read()
        fakefile = FakeFile()    
        fakefile.write(data)
        return fakefile
    
    def afterSetUp(self):
        """
        Run before tests
        """
        # basic data
        self.folder_url = self.folder.absolute_url()
        self.folder_path = '/%s' % self.folder.absolute_url(1)
        self.basic_auth = '%s:%s' % (default_user, default_password)
        self.owner_auth = '%s:%s' % (portal_owner, default_password)
        
    def test_createObject(self):
        """
        Create an object using the createObject script
        """
        
        response = self.publish(self.folder_path +
                                '/createObject?type_name=%s' % self.portal_type,
                                self.basic_auth)
        self.assertEqual(response.getStatus(), 302) # Redirect to edit

        # omit ?portal_status_message=...
        url = response.getBody().split('?')[0]

        self.failUnless(url.startswith(self.folder_url))
        # The url may end with /edit or /atct_edit depending on method aliases
        self.failUnless(url.endswith('edit'))

        # Perform the redirect
        edit_form_path = url[len(self.app.REQUEST.SERVER_URL):]
        response = self.publish(edit_form_path, self.basic_auth)
        self.assertEqual(response.getStatus(), 200) # OK
        temp_id = url.split('/')[-2]
        new_obj = getattr(self.folder.portal_factory, temp_id)
        self.failUnlessEqual(new_obj.checkCreationFlag(), True) # object is not yet edited
    
    def test_edit_view(self):
        """
        Edit tab template
        """
        self.folder.invokeFactory(self.portal_type, self.object_id)
        obj = getattr(self.folder, self.object_id)
        path = '/%s/atct_edit' % obj.absolute_url(1)
        response = self.publish(path, self.basic_auth)
        self.assertEqual(response.getStatus(), 200) # OK

    def test_metadata_edit_view(self):
        """
        Metadata tab template
        """
        self.folder.invokeFactory(self.portal_type, self.object_id)
        obj = getattr(self.folder, self.object_id)
        path = '/%s/base_metadata' % obj.absolute_url(1)
        response = self.publish(path, self.basic_auth)
        self.assertEqual(response.getStatus(), 200) # OK

    def test_base_view(self):
        """
        Base view tab template
        """
        self.folder.invokeFactory(self.portal_type, self.object_id)
        obj = getattr(self.folder, self.object_id)
        path = '/%s/base_view' % obj.absolute_url(1)
        response = self.publish(path, self.basic_auth)
        self.assertEqual(response.getStatus(), 200) # OK
    
    def test_view(self):
        """
        Dynamic 'view' template
        """
        self.folder.invokeFactory(self.portal_type, self.object_id)
        obj = getattr(self.folder, self.object_id)
        path = '/%s/view' % obj.absolute_url(1)
        response = self.publish(path, self.basic_auth)
        self.assertEqual(response.getStatus(), 200) # OK
        
    def test_folder_localrole_form(self):
        """
        Sharing tab template
        """
        self.folder.invokeFactory(self.portal_type, self.object_id)
        obj = getattr(self.folder, self.object_id)
        path = '/%s/folder_localrole_form' % obj.absolute_url(1)
        response = self.publish(path, self.basic_auth)
        #Plone <=2.5 returns 200, 3.0 returns 302
        self.failUnless(response.getStatus() in (200, 302))


