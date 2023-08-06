"""Testcases for cssutils.scripts.csscombine"""
__version__ = '$Id: test_scripts_csscombine.py 1755 2009-05-30 14:50:35Z cthedot $'

from cssutils.script import csscombine
import basetest
import cssutils
import os

class CSSCombine(basetest.BaseTestCase):

    C = '@namespace s2"uri";s2|sheet-1{top:1px}s2|sheet-2{top:2px}proxy{top:3px}' 

    def test_combine(self):
        "scripts.csscombine"        
        # path, SHOULD be keyword argument!
        csspath = os.path.join(os.path.dirname(__file__), '..', '..', 
                               'sheets', 'csscombine-proxy.css')
        combined = csscombine(csspath)
        self.assertEqual(combined, self.C)
        combined = csscombine(path=csspath, targetencoding='ascii')
        self.assertEqual(combined, '@charset "ascii";' + self.C)

        # url
        cssurl = cssutils.helper.path2url(csspath)
        combined = csscombine(url=cssurl)
        self.assertEqual(combined, self.C)
        combined = csscombine(url=cssurl, targetencoding='ascii')
        self.assertEqual(combined, '@charset "ascii";' + self.C)

        cssutils.log.raiseExceptions = True 


if __name__ == '__main__':
    import unittest
    unittest.main()
