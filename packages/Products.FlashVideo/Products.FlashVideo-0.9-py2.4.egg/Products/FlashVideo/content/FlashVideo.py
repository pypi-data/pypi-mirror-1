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
import types

# Zope
from AccessControl import ClassSecurityInfo
from Acquisition import aq_inner
from Acquisition import aq_parent

from Products.CMFCore.permissions import View
from Products.CMFCore.permissions import ModifyPortalContent
from Products.ATContentTypes.content.file import ATFile
from Products.ATContentTypes.interfaces import IATFile
from Products.ATContentTypes.content.schemata import ATContentTypeSchema
from Products.ATContentTypes.content.schemata import finalizeATCTSchema
from Products.validation import V_REQUIRED
#Try multilingual support
#try:
    #from Products.LinguaPlone.public import *
#except ImportError:
from Products.Archetypes.public import *
#Try external storage
try:
    from Products.FileSystemStorage.FileSystemStorage import FileSystemStorage
    STORAGE = FileSystemStorage()
except:
    STORAGE = AnnotationStorage(migrate=True)

#Product
from Products.FlashVideo.config import *
from Products.FlashVideo.FLVHeader import FLVHeader

FlashVideoSchema = ATContentTypeSchema.copy() + Schema((

    FileField('file',
              required=True,
              primary=True,
              languageIndependent=True,
              storage = STORAGE,
              validators = (('isNonEmptyFile', V_REQUIRED),
                            'isFLVFile',),
              widget = FileWidget(label= "Movie File",                                  
                                  description = "Select Flash movie file (*.flv)",
                                  label_msgid = "label_movie_file",
                                  description_msgid = "help_movie_file",                        
                                  i18n_domain = "plone",),
              ),

    ImageField('screenshot',
               required = False,
               storage = AnnotationStorage(migrate=True),
               sizes= {'mini'    : (200, 200),
                       'thumb'   : (128, 128),
                       'tile'    :  (64, 64),
                       'icon'    :  (32, 32),
                      },
               validators = (('isNonEmptyFile', V_REQUIRED),),
               widget = ImageWidget(label= "Screenshot",
                                    description = "Image that will be shown when movie is not playing. \
                                    Shoud have the same resolution as movie.",
                                    label_msgid = "label_screenshot",
                                    description_msgid = "help_screenshot",                        
                                    i18n_domain = "plone",)
               ),
    
    StringField('width',
                searchable=0,
                widget=IntegerWidget(label='Movie/screenshot width',
                                     description='Enter movie width',
                                     label_msgid = "label_movie_width",
                                     description_msgid = "help_movie_width",                        
                                     i18n_domain = "plone",),
                ),
    
    StringField('height',
                searchable=0,
                widget=IntegerWidget(label='Movie/screenshot height',
                                     description='Enter movie height',
                                     label_msgid = "label_movie_height",
                                     description_msgid = "help_movie_height",                        
                                     i18n_domain = "plone",),
                ),
    
    ),
    #marshall=PrimaryFieldMarshaller()
    )

finalizeATCTSchema(FlashVideoSchema)

class FlashVideo(ATFile):    
    schema                = FlashVideoSchema
    content_icon          = 'flashvideo_icon.gif'
    meta_type             = FLASHVIDEO_METATYPE
    portal_type           = FLASHVIDEO_PORTALTYPE
    archetype_name        = FLASHVIDEO_PORTALTYPE
    allowed_content_types = ()
    filter_content_types  = False
    immediate_view        = 'flashvideo_view'
    default_view          = 'flashvideo_view'
    typeDescription       = 'Flash video (*.flv) file that can be viewed in player.'
    typeDescMsgId         = 'description_type_flashvideo'
    _at_rename_after_creation = True
    
    __implements__ = ATFile.__implements__, IATFile
    security       = ClassSecurityInfo()        
            
    def manage_afterPUT(self, data, marshall_data, file, context, mimetype,
                        filename, REQUEST, RESPONSE):
        """After WebDAV/FTP PUT method
        Prevent name from having dots inside for Flash Video objects.
        Flow Player doesn't like that.
        """
        id = self.getId()
        if id.endswith(".flv"):
            new_id = id.replace(".flv","").replace(".","_")
        else:
            new_id = id.replace(".","_")
        title = new_id.replace("-"," ").replace("_"," ").capitalize()
        if id != new_id:            
            self.setId(new_id)
            self.setTitle(title)

    def __bobo_traverse__(self, REQUEST, name):
        """Transparent access to image scales"""        
        if name.startswith('screenshot'):
            #print "__bobo_traverse__", name
            field = self.getField('screenshot')
            image = None
            if name in ('screenshot',):                
                image = field.getScale(self)
            else:
                scalename = name[len('screenshot_'):]
                if scalename in field.getAvailableSizes(self):
                    image = field.getScale(self, scale=scalename)
            if image is not None and not isinstance(image, basestring):
                return image
        return ATFile.__bobo_traverse__(self, REQUEST, name)

    def _setATCTFileContent(self, value, **kwargs):
        """Override method from ATCTFileContent. Removed part that renames
        object according to file name. BaseObject._renameAfterCreation
        will use title as id.
        """
        field = self.getPrimaryField()
        field.set(self, value, **kwargs)
                  
    def getMovieWidth(self):
        """Get movie width. If property not set check width
        of screenshot.
        """        
        width_field = self.getField('width')
        width = width_field.get(self)
        if not width:
            screenshot_field = self.getField('screenshot')
            if screenshot_field:
                image = screenshot_field.getScale(self)
                if image:
                    width = image.width
        if not width:
            width = DEFAULT_VIDEO_WIDTH
        return int(width)

    def getMovieHeight(self):
        """Get movie height. If property not set check height
        of screenshot.
        """
        height_field = self.getField('height')
        height = height_field.get(self)
        if not height:
            screenshot_field = self.getField('screenshot')
            if screenshot_field:
                image = screenshot_field.getScale(self)
                if image:
                    height = image.height
        if not height:
            height = DEFAULT_VIDEO_HEIGHT
        return int(height)
    
    security.declareProtected(ModifyPortalContent, 'setFile')
    def setFile(self, value, **kwargs):
        """Saves file and gets flash informations (size, flash version)"""
        #print "setFile",type(value)
        ATFile.setFile(self, value, **kwargs)        
        if value:            
            # If called via webDAV value is string not file
            if type(value) in (types.StringType, types.UnicodeType):
                # String passed from WebDAV
                header = value[:1024]
            else:
                # Normal uploaded file
                value.seek(0) # rewind
                header = value.read(1024)
            flvparser = FLVHeader()
            flvparser.analyse(header)
            width = flvparser.getWidth()
            height = flvparser.getHeight()
            if width:
                self.setWidth(width)
            if height:
                self.setHeight(height)
            
    security.declareProtected(ModifyPortalContent, 'setWidth')
    def setWidth(self, value, **kwargs):
        """Don't allow to reset width after automatically set in setFile"""
        field = self.getField('width')
        if field:
            old_value = field.get(self)
            if old_value and not value:                
                return
        field.set(self, value)
        
    security.declareProtected(ModifyPortalContent, 'setHeight')
    def setHeight(self, value, **kwargs):
        """Don't allow to reset height after automatically set in setFile"""
        field = self.getField('height')
        if field:
            old_value = field.get(self)
            if old_value and not value:                
                return
        field.set(self, value)
       
    security.declareProtected(View, 'hasScreenshot') 
    def hasScreenshot(self):
        """Simple method for testing if screenshot was uploaded"""
        if self.getScreenshot():
            return True
        else:
            return False
         
    security.declareProtected(View, 'getConfigString')
    def getConfigString(self):
        """Dynamically generate config string for swfplayer
        depending if screenshot is defined or not 
        """
        if self.hasScreenshot():
            image_str = "{url: '%s/screenshot', overlayId: \'play\'}, "%(
                self.absolute_url())
        else:
            image_str = ""
        file_str = "{url: '%s', type: \'flv\'}"%(self.absolute_url())
        config_str ="{playList: [%s%s], autoRewind: true, \
            initialScale: \'fit\', loop: false, autoPlay: false}"%(
                image_str, file_str)
        return config_str
    
    #def __repr__(self):
        #return "<FlashVideo>"
        
registerType(FlashVideo,PROJECTNAME)
