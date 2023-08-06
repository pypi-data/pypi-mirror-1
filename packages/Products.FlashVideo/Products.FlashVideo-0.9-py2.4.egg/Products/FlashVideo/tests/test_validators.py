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
Unit tests for validators
"""

import unittest
import sys
import os
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py')) 
    
from Products.FlashVideo.validators import FLVValidator
from BaseTest import FakeFile

class FLVValidatorTests(unittest.TestCase):
    """
    Test class for FLVValidator class
    """   
    
    def _readFile(self, name="test_movie.flv", data=None):
        """
        """
        #Trick to get absolute path
        if not data:
            ihome = os.environ.get('INSTANCE_HOME')
            path = os.path.join(ihome,"Products","FlashVideo","tests",name)
            data = file(path,"r").read()
        fakefile = FakeFile()
        fakefile.write(data)
        fakefile.seek(0)
        return fakefile
    
    
    def test_init(self):
        """
        Simple class instance
        """
        validator = FLVValidator("isFLVFile")
        self.assertEqual(getattr(validator,'name',''),"isFLVFile")
        
    def test__call__good(self):
        """
        Test __call__ method with correct file
        """
        validator = FLVValidator("isFLVFile")
        flv_file = self._readFile()
        
        result = validator.__call__(flv_file)
        self.assertEqual(result, 1)
        
    def test__call__bad(self):
        """
        Test __call__ method with incorrect file
        """
        validator = FLVValidator("isFLVFile")
        #bad type        
        flv_file = self._readFile(name="test_movie.jpg")
        result = validator.__call__(flv_file)
        self.assertEqual(result, "This does not appear to be an FLV file")
        #bad length        
        flv_file2 = self._readFile(data="FLV1234")
        result = validator.__call__(flv_file2)
        self.assertEqual(result, "Data size too small")
            
        
def test_suite():
    """
    Build test suite
    """  
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(sys.modules[__name__])
    return suite

def main():
    """
    Run tests
    """  
    unittest.TextTestRunner().run( test_suite() )

if __name__ == '__main__':
    main()