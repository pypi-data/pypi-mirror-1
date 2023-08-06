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
Unit tests for FLVHeader
"""

import unittest
import sys
import os
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py')) 
    
from Products.FlashVideo.FLVHeader import FLVHeader
from Products.FlashVideo.FLVHeader import FLVHeaderError

class FLVHeaderTests(unittest.TestCase):
    """
    Test class for FLVHeader class
    """   
    
    def _readFile(self):
        """
        """
        #Trick to get absolute path
        ihome = os.environ.get('INSTANCE_HOME')
        path = os.path.join(ihome,"Products","FlashVideo","tests","test_movie.flv")
        data = file(path,"r").read()
        return data
    
    def test_init(self):
        """
        Simple class instance
        """
        flv = FLVHeader()
        self.assertEqual(hasattr(flv,'width'),True)
        self.assertEqual(hasattr(flv,'height'),True)
        
    def test_wrongData(self):
        """
        Wrong input data
        """
        flv = FLVHeader()
        # Data to small
        self.assertRaises(FLVHeaderError, flv.analyse, data="FLV")
        # Wrong header
        self.assertRaises(FLVHeaderError, flv.analyse, data="SWF"+"x"*100)
        
    def test_bin2float(self):
        """
        Dummy test to convert binary data to float
        """
        flv = FLVHeader()
        bin130 = '\x40\x60\x40\x00\x00\x00\x00\x00'
        self.assertEqual(flv.bin2float(bin130),130.0)
        bin70 = '\x40\x51\x80\x00\x00\x00\x00\x00'
        self.assertEqual(flv.bin2float(bin70),70.0)
        
    def test_getHeight(self):
        """
        Get height
        """
        flv = FLVHeader()
        self.assertEqual(flv.getHeight(),None)
        flv.height = 123.1
        self.assertEqual(flv.getHeight(),123)
        
    def test_getWidth(self):
        """
        Get width
        """
        flv = FLVHeader()
        self.assertEqual(flv.getWidth(),None)
        flv.width = 123.1
        self.assertEqual(flv.getWidth(),123)        
        
    def test_getFlag(self):
        """
        Get flag from dictionary
        """
        flv = FLVHeader()
        self.assertEqual(flv.getFlag(1),'video')
        self.assertEqual(flv.getFlag(4),'audio')
        self.assertEqual(flv.getFlag(5),'audio + video')
        self.assertEqual(flv.getFlag(6),None)
             
    def test_getTagType(self):
        """
        Get tag types from dictionary
        """
        flv = FLVHeader()
        self.assertEqual(flv.getTagType('0x8'),'audio')
        self.assertEqual(flv.getTagType('0x9'),'video')
        self.assertEqual(flv.getTagType('0x12'),'meta')

    def test_getAmfType(self):
        """
        Get AMF tag from dictionary. Not all tags are there, only those
        used in FLV
        """
        flv = FLVHeader()
        self.assertEqual(flv.getAmfType('0x0'),'number')
        self.assertEqual(flv.getAmfType('0x1'),'boolean')
        self.assertEqual(flv.getAmfType('0x2'),'string')
        self.assertEqual(flv.getAmfType('0x8'),'mixed array')
        self.assertEqual(flv.getAmfType('0xb'),'date')
        self.assertEqual(flv.getAmfType('0xc'),'long string')

    def test_analyseContent(self):
        """
        Read metatags from sample file
        """
        flv = FLVHeader()
        data = self._readFile()
        meta = flv.analyseContent(data)
        self.assertEqual(meta['width'],130.0)
        self.assertEqual(meta['height'],70.0)
        self.assertEqual(meta['audiosize'],70920.0)
        self.assertEqual(meta['filesize'],282797.0)
        self.assertEqual(meta['duration'],20.584)
        self.assertEqual(meta['creationdate'],'unknown')
        self.assertEqual(meta['videosize'],206323.0)
        self.assertEqual(meta['datasize'],333.0)
        self.assertEqual(meta['framerate'],39.922027290448341)
        self.assertEqual(meta['metadatadate'],None)
        
    def test_analyse(self):
        """
        Process sample file, read width and height
        """
        flv = FLVHeader()
        data = self._readFile()
        flv.analyse(data)
        self.assertEqual(flv.getWidth(),130)
        self.assertEqual(flv.getHeight(),70)        
         
        
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