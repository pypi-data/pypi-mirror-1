# -*- coding: utf-8 -*-
"""
testcases for cssutils.css.CSSRuleList
"""
__author__ = '$LastChangedBy: cthedot $'
__date__ = '$LastChangedDate: 2007-10-19 15:10:03 +0200 (Fr, 19 Okt 2007) $'
__version__ = '$LastChangedRevision: 535 $'

import basetest
import cssutils

class CSSRuleListTestCase(basetest.BaseTestCase):

    def test_init(self):
        "CSSRuleList init"
        r = cssutils.css.CSSRuleList()
        self.assertEqual(0, r.length)
        self.assertEqual(None, r.item(2))

        # subclasses list!
        r.append(0)
        r.append(1)
        self.assertEqual(2, r.length)
        self.assertEqual(1, r.item(1))
        self.assertEqual(None, r.item(2))


if __name__ == '__main__':
    import unittest
    unittest.main()
