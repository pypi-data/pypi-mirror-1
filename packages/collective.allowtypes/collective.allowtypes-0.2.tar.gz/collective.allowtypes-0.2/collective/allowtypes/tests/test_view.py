# -*- coding: utf-8 -*-
#
# File: test_view.py
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

__author__    = 'Ramon Bartl <ramon.bartl@inquant.de>'
__docformat__ = 'plaintext'

from zope.component import queryMultiAdapter

from base import PackageTestCase


class TestView(PackageTestCase):

    def afterSetUp(self):
        self.view = queryMultiAdapter((self.portal, self.portal.REQUEST),
                name="allowtypes")

    def test_document_allowed_under_folder(self):
        self.failUnless('Document' in [t['type'] for t in self.view.allowed(self.folder)])


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestView))
    return suite

# vim: set ft=python ts=4 sw=4 expandtab :
