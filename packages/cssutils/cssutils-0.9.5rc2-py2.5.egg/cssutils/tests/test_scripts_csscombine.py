"""Testcases for cssutils.scripts.csscombine"""
__version__ = '$Id: test_scripts_csscombine.py 1116 2008-03-05 13:52:23Z cthedot $'

import os
import basetest
from cssutils.scripts import csscombine
import cssutils

class CSSCombine(basetest.BaseTestCase):

    def test_combine(self):
        "scripts.csscombine"
        csspath = os.path.join(os.path.dirname(__file__), '..', '..', '..', 
                               'sheets', 'csscombine-proxy.css')
        combined = csscombine(csspath)
        self.assertEqual(combined, 
                         '@charset "utf-8";a{color:green}body{color:#fff;background:#000}' 
                         )
        combined = csscombine(csspath, targetencoding='ascii')
        self.assertEqual(combined, 
                         '@charset "ascii";a{color:green}body{color:#fff;background:#000}' 
                         )

        cssutils.log.raiseExceptions = True 

    def tearDown(self):
        # needs to be re-enabled here for other tests
        cssutils.log.raiseExceptions = True
        # no needed as csscombine uses own serializer
        # cssutils.ser.prefs.useDefaults() 


if __name__ == '__main__':
    import unittest
    unittest.main()
