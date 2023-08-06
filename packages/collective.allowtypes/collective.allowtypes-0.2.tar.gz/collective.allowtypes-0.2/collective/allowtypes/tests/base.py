# -*- coding: utf-8 -*-
#
# File: base.py
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

from Products.Five import zcml
from Products.Five import fiveconfigure

from Testing import ZopeTestCase as ztc

from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import onsetup

import collective.allowtypes

@onsetup
def setup_collective_allowtypes():
    """Set up the additional products
    """

    fiveconfigure.debug_mode = True
    zcml.load_config('configure.zcml', collective.allowtypes)
    fiveconfigure.debug_mode = False

    # install Products
    #ztc.installProduct('')

    # install Packages
    ztc.installPackage('collective.allowtypes')

setup_collective_allowtypes()

ptc.setupPloneSite(products=['collective.allowtypes'])


class PackageTestCase(ptc.PloneTestCase):
    """Base class used for test cases
    """

class PackageFunctionalTestCase(ptc.FunctionalTestCase):
    """Test case class used for functional (doc-)tests
    """

# vim: set ft=python ts=4 sw=4 expandtab :
