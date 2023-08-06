##############################################################################
#
# Copyright (c) 2006 Lovely Systems and Contributors.
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

from Products.Five import fiveconfigure
from Products.Five import zcml
from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import onsetup
from Testing import ZopeTestCase as ztc

import doctest
import unittest

@onsetup
def load_package_products():
    import z3c.zrtresource

    fiveconfigure.debug_mode = True
    zcml.load_config('meta.zcml', z3c.zrtresource)
    fiveconfigure.debug_mode = False

load_package_products()
ptc.setupPloneSite(products=['collective.zrtresource'])

class ResourceTestCase(ptc.FunctionalTestCase):
    """ Test case for z3c.zrtresource. """

def test_suite():

    return unittest.TestSuite((
        ztc.FunctionalDocFileSuite('README.txt',
                     package='collective.zrtresource',
                     optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
                     test_class=ResourceTestCase,
                     ),
        ztc.FunctionalDocFileSuite('zcml.txt',
                     package='collective.zrtresource',
                     optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
                     test_class=ResourceTestCase,
                     ),
        ))
