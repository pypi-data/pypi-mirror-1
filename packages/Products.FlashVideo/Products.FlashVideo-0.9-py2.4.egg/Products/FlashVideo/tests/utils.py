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

import os
from sys import stdin, stdout
from ZPublisher.HTTPRequest import HTTPRequest
from ZPublisher.HTTPResponse import HTTPResponse

def getRequest():
    resp = HTTPResponse(stdout=stdout)
    environ = os.environ.copy()
    environ['SERVER_NAME'] = 'foo'
    environ['SERVER_PORT'] = '80'
    environ['REQUEST_METHOD'] =  'GET'
    req = HTTPRequest(stdin, environ, resp)
    req._steps = ['noobject']  # Fake a published object.
    req['ACTUAL_URL'] = req.get('URL') # Zope 2.7.4
    return req