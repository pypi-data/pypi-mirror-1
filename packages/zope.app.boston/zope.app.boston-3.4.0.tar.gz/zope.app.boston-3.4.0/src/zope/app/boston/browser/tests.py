##############################################################################
#
# Copyright (c) 2005 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Boston skin ftests

$Id: tests.py 81497 2007-11-04 23:53:30Z srichter $
"""

import unittest

from zope.app.testing.functional import BrowserTestCase
from zope.app.boston.testing import BostonLayer

class TestBostonSkin(BrowserTestCase):


    def test_addFolder(self):
        response = self.publish(
            "/++skin++Boston/+/action.html",
            basic='mgr:mgrpw',
            form={'type_name':u'zope.app.content.Folder',
                  'id':u'folder'})
        self.assertEqual(response.getStatus(), 302)

        response = self.publish(
            "/++skin++Boston/folder/+/action.html",
            basic='mgr:mgrpw',
            form={'type_name':u'zope.app.content.Folder',
                  'id':u'subfolder'})
        self.assertEqual(response.getStatus(), 302)

    def test_addSiteManager(self):
        response = self.publish(
            "/++skin++Boston/+/action.html",
            basic='mgr:mgrpw',
            form={'type_name':u'zope.app.content.Folder',
                  'id':u'folder'})
        self.assertEqual(response.getStatus(), 302)

        response = self.publish(
            "/++skin++Boston/folder/+/action.html",
            basic='mgr:mgrpw',
            form={'type_name':u'zope.app.content.Folder',
                  'id':u'subsite'})
        self.assertEqual(response.getStatus(), 302)

        response = self.publish(
            "/++skin++Boston/folder/subsite/addSiteManager.html",
            basic='mgr:mgrpw')
        self.assertEqual(response.getStatus(), 302)

    def test_css_pagelets(self):
        response = self.publish('/++skin++Boston/', basic='mgr:mgrpw')
        self.assertEqual(response.getStatus(), 200)
        self.assert_(response.getBody().find(
            'href="http://localhost/++skin++Boston/@@/skin.css"') != -1)
        self.assert_(response.getBody().find(
            'href="http://localhost/++skin++Boston/@@/widget.css"') != -1)

    def test_javascrip_pagelets(self):
        response = self.publish('/++skin++Boston/', basic='mgr:mgrpw')
        self.assertEqual(response.getStatus(), 200)
        self.assert_(response.getBody().find(
            'src="http://localhost/++skin++Boston/@@/boston.js"') != -1)

    def test_left_boxes(self):
        # Add a folder
        response = self.publish(
            "/++skin++Boston/+/action.html",
            basic='mgr:mgrpw',
            form={'type_name':u'zope.app.content.Folder',
                  'id':u'folder'})
        self.assertEqual(response.getStatus(), 302)

        response = self.publish('/++skin++Boston/', basic='mgr:mgrpw')
        self.assertEqual(response.getStatus(), 200)

        # test xmltree box
        self.assert_(response.getBody().find('id="xmltree"') != -1)

        # test addinginfo box
        self.assert_(response.getBody().find('id="addinginfo"') != -1)


def test_suite():
    suite = unittest.TestSuite()
    TestBostonSkin.layer = BostonLayer
    suite.addTest(unittest.makeSuite(TestBostonSkin))
    return suite

if __name__=='__main__':
    unittest.main(defaultTest='test_suite')

