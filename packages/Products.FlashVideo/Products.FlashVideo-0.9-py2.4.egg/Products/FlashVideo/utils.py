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

from copy import copy

IS_PLONE_21 = False
IS_PLONE_25 = False
IS_PLONE_30 = False
IS_PLONE_31 = False
try:
    from Products.CMFPlone.migrations import v2_1
    IS_PLONE_21 = True
except ImportError:
    pass
try:
    from Products.CMFPlone.migrations import v2_5
    IS_PLONE_21 = False
    IS_PLONE_25 = True
except ImportError:
    pass
try:
    from Products.CMFPlone.migrations import v3_0
    IS_PLONE_21 = False
    IS_PLONE_25 = False
    IS_PLONE_30 = True
except ImportError:
    pass
try:
    from Products.CMFPlone.migrations import v3_1
    IS_PLONE_21 = False
    IS_PLONE_25 = False
    IS_PLONE_30 = False
    IS_PLONE_31 = True
except ImportError:
    pass
    
def updateActions(klass, actions):
    """
    Merge the actions from a class with a list of actions.
    Copied from ATcontentTypes because it doesn't exists in Plone3
    """
    if hasattr(klass,'actions'):
        kactions = copy(klass.actions)
        aids  = [action.get('id') for action in actions ]
        actions = list(actions)
        for kaction in kactions:
            kaid = kaction.get('id')
            if kaid not in aids:
                actions.append(kaction)
    
        return tuple(actions)
    else:
        #Plone 3 has no actions. It will be initialized in XML
        return ()