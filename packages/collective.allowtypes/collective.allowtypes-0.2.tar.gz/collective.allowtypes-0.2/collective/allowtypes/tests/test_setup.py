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

__author__ = 'Ramon Bartl <ramon.bartl@inquant.de>'
__docformat__ = 'plaintext'

from Products.CMFCore.utils import getToolByName

from zope.component import queryMultiAdapter

from base import PackageTestCase

class TestSetup(PackageTestCase):

    def test_view_registered(self):
        view = queryMultiAdapter((self.portal, self.portal.REQUEST),
                name='allowtypes')
        self.failUnless(view is not None)

    def test_configlet_registered(self):
        cp = getToolByName(self.portal, 'portal_controlpanel')
        self.failUnless('allowtypesconfiglet' in [
            action.getId() for action in cp.listActions()])


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestSetup))
    return suite

# vim: set ft=python ts=4 sw=4 expandtab :
