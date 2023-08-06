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

#Python
from cStringIO import StringIO

#Zope
from Products.Archetypes.Extensions.utils import install_subskin
from Products.Archetypes import listTypes
from Products.Archetypes.Extensions.utils import installTypes
from Products.CMFCore.utils import getToolByName

#Product
from Products.FlashVideo.config import *
from Products.FlashVideo.utils import IS_PLONE_30
from Products.FlashVideo.utils import IS_PLONE_31

def install(self):
    out = StringIO()
    portal = getToolByName(self,'portal_url').getPortalObject()
    portal_setup = getToolByName(portal, 'portal_setup', None)
    
    # Plone >= 2.5
    if portal_setup:
        print >> out, "Installation using Generic Setup"
        # Plone >= 3.0
        if hasattr(portal_setup, 'runAllImportStepsFromProfile'):
            portal_setup.runAllImportStepsFromProfile('profile-FlashVideo:default')
        else:
            # Plone == 2.5
            old_context = portal_setup.getImportContextID()
            portal_setup.setImportContext('profile-FlashVideo:default')
            portal_setup.runAllImportSteps()
            portal_setup.setImportContext(old_context)
    # Plone <= 2.1
    else:
        print >> out, "Ordinary installation"
        installFSS(portal, out)
        installPloneTypes(portal, out, PROJECTNAME)
        install_subskin(portal, out, GLOBALS)
        hideTypesInNavigation(portal, out)    
        addViewActions(portal, out)
        registerMimeType(portal, out)
        registerContentType(portal, out)
        
    print >> out, "Installation completed."
    return out.getvalue()

def installPloneTypes(portal, out, projectname):
    """
    Register Archetype content types
    """
    typeInfo = listTypes(projectname)
    installTypes(portal, out,
                 typeInfo,
                 projectname)
    print >> out, "Types registered"

def addViewActions(portal, out):
    """
    """
    portal_properties = getToolByName(portal,'portal_properties')
    site_properties = portal_properties.site_properties
    actions = list(site_properties.getProperty('typesUseViewActionInListings', ()))
    for t in (FLASHVIDEO_PORTALTYPE,):
        if t not in actions:
            actions.append(t)
    site_properties.typesUseViewActionInListings = tuple(actions)
    print >> out, "View actions in listings updated" 
    
def installFSS(portal, out = None):
    """
    Install FileSystemStorage if exists
    """
    if not out:
        #Hook to work from GenericSetup
        portal = portal.getSite()
        out = StringIO()
    root = portal.getPhysicalRoot()
    
    #This is necessary tests to work without FSS
    Products = root.Control_Panel.Products
    portal_quickinstaller=getToolByName(portal, 'portal_quickinstaller', None)
    
    if 'FileSystemStorage' in Products.objectIds():
        if portal_quickinstaller.isProductInstallable('FileSystemStorage'):
            if not portal_quickinstaller.isProductInstalled('FileSystemStorage'):
                portal_quickinstaller.installProduct('FileSystemStorage')
                print >>out, 'Installing FileSystemStorage'
            else:
                print >>out, 'FileSystemStorage already installed.'
        else:
            print >>out, 'FileSystemStorage not installable.'
    else:
        print >>out, 'FileSystemStorage Product not added.'
        
def hideTypesInNavigation(portal, out):
    """
    Hide selected types from the navtree
    """
    portal_properties = getToolByName(portal, 'portal_properties', None)
    navtree_properties = portal_properties.navtree_properties
    hidden_list = (FLASHVIDEO_PORTALTYPE,)
    types_not_to_list = list(navtree_properties.getProperty('metaTypesNotToList', ()))
    for t in hidden_list:
        if t not in types_not_to_list:
            types_not_to_list.append(t)
    navtree_properties._setPropValue('metaTypesNotToList',types_not_to_list)
    print >>out, 'Types hidden from navigation: %s'%(", ".join(hidden_list))
    
def removeDuplicateActionsInTypes(portal, out = None):
    """
    In Plone 3 xml configuraton adds duplicated 'local_roles' action.
    Remove it
    """
    if not out:
        #Hook to work from GenericSetup
        portal = portal.getSite()
        out = StringIO()
    if IS_PLONE_30 or IS_PLONE_31:
        portal_types = getToolByName(portal, 'portal_types', None)
        for portal_type in (FLASHVIDEO_PORTALTYPE,
                            FLASHVIDEOFOLDER_PORTALTYPE,
                            FLASHVIDEOPLAYLIST_PORTALTYPE):
            p_type = portal_types.getTypeInfo(portal_type)
            type_actions = p_type._actions
            actions_ids = [x.getId() for x in type_actions]
            for i in range(len(type_actions)):
                action = type_actions[i]
                expr = action.getActionExpression() 
                if hasattr(expr,'text'):
                    expr = expr.text
                if action.getId() == 'local_roles' and expr == 'string:${object_url}/sharing':
                    p_type.deleteActions(selections=(actions_ids.index('local_roles'),))
                    print >>out, "Duplicate 'local_roles' action from '%s' deleted"%(portal_type)
                    break
   
def registerMimeType(portal, out = None):
    """
    Adds information to mimetypes_registry
    """
    if not out:
        # Hook to work from GenericSetup
        portal = portal.getSite()
        out = StringIO()
    info = {'id':'Flash Video','mimetypes':['video/x-flv'],
            'extensions':['flv',],'icon_path':'flashvideo_icon.gif',
            'binary':True,'globs':['*.flv',]}
    mimetypes_registry = getToolByName(portal,'mimetypes_registry')
    if not mimetypes_registry.lookup(info['mimetypes']):
        mimetypes_registry.manage_addMimeType(**info)
        print >>out, "MIME type '%s' added to register"%(info['id'])
    else:
        print >>out, "MIME type '%s' already in register"%(info['id'])

def registerContentType(portal, out = None):
    """
    Adds information to content_type_registry
    """
    if not out:
        #Hook to work from GenericSetup
        portal = portal.getSite()
        out = StringIO()
    infos = [
        {'id':'flv','type':'extension', 'extensions':'flv',
         'portal_type':'Flash Video'},
        {'id':'video/x-flv','type':'major_minor',
         'major':'video','minor':'x-flv', 
         'portal_type':'Flash Video'},
        ]
    content_type_registry = getToolByName(portal,'content_type_registry')
    predicate_ids = content_type_registry.predicate_ids
    for info in infos:
        if not info['id'] in predicate_ids:
            content_type_registry.addPredicate(info['id'],info['type'])
            predicate = content_type_registry.getPredicate(info['id'])
            if info['type'] == 'extension':
                predicate.edit(info['extensions'])        
            elif info['type'] == 'major_minor':
                predicate.edit(info['major'],info['minor'])
            content_type_registry.assignTypeName(info['id'], info['portal_type'])
            print >>out, "Predicate '%s': '%s' for '%s' added to register"%(
                    info['id'], info['type'], info['portal_type'])
        else:
            print >>out, "Predicate '%s': '%s' for '%s' already exists in register"%(
                    info['id'], info['type'], info['portal_type'])
        
    content_type_registry.reorderPredicate('video', 
        len(content_type_registry.listPredicates())-1) 
    print >>out, "Predicate 'video' moved to bottom of register"
    
#def uninstall_selection(portal, out, product_skins_dir='skins',
                        #forbidden_selections=()):
    #print "uninstall_selection"
    #portal_skins = getToolByName(portal, 'portal_skins')
    #selections = portal_skins.getSkinSelections()
    #print selections
    ##layers = 
    
    