# -*- coding: utf-8 -*-
#
# File: test_setup.py
#
# Copyright (c) InQuant GmbH
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

__author__    = """Ramon Bartl <ramon.bartl@inquant.de>"""
__docformat__ = 'plaintext'
__revision__  = "$Revision: 66382 $"
__version__   = '$Revision: 66382 $'[11:-2]

import unittest
from collective.plone.gsxml.tests.base import GSXMLTestCase
from Products.CMFCore.utils import getToolByName

class TestSetup(GSXMLTestCase):

    def afterSetUp(self):
        self.setRoles(('Manager',))
        self.actions = getToolByName(self.portal, 'portal_actions')

    def test_export_action(self):
        ac = self.actions["object_buttons"]
        self.failUnless(getattr(ac, "xmlexport", None))

    def test_import_action(self):
        ac = self.actions["object_buttons"]
        self.failUnless(getattr(ac, "xmlimport", None))

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestSetup))
    return suite

# vim: set ft=python ts=4 sw=4 expandtab :
