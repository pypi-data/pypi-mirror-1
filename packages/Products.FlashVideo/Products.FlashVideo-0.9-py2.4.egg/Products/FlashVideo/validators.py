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

from Products.validation.interfaces import ivalidator

class FLVValidator:
    __implements__ = (ivalidator,)

    def __init__(self, name):
        self.name = name

    def __call__(self, fileupload, *args, **kwargs):
        msg = None
        # Do only for 'ZPublisher.HTTPRequest.FileUpload' instance -
        # which is used if new file is uploaded. If file already exists
        # parameter is 'OFS.Image.File' object and there is no 'read' method.
        if hasattr(fileupload,'read'):
            # Check only when object is created
            data = fileupload.read()
            signature = data[:3] #always FLV
            if not str(signature) == 'FLV':
                msg = "This does not appear to be an FLV file"
            elif len(data)<=(8+17):
                msg = "Data size too small"
            if msg:
                return (msg)
        return 1