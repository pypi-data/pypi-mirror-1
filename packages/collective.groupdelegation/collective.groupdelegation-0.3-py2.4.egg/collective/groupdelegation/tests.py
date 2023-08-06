# -*- coding: utf-8 -*-
## Copyright (C) 2009 Ingeniweb - all rights reserved    

## This program is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 2 of the License, or
## (at your option) any later version.

## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.

## You should have received a copy of the GNU General Public License
## along with this program; see the file COPYING. If not, write to the
## Free Software Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.

import sys
import unittest
from zope.testing import doctest
from zope.testing import doctestunit
from zope.component import testing
from Testing import ZopeTestCase as ztc

from Products.Five import zcml
from Products.Five import fiveconfigure
from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import PloneSite

from Products.PloneTestCase.layer import onsetup


@onsetup
def setup_product():
    """
    Set up the package and its dependencies.
    """    
    fiveconfigure.debug_mode = True
    import collective.groupdelegation
    zcml.load_config('configure.zcml',collective.groupdelegation)
    fiveconfigure.debug_mode = False    
    ztc.installPackage('collective.groupdelegation')    

setup_product()
ptc.setupPloneSite()


class TestCase(ptc.FunctionalTestCase):
    class layer(PloneSite):
        @classmethod
        def setUp(cls):
            # doctests don't play nicely with ipython
            try :
                iphook = sys.displayhook
                sys.displayhook = sys.__displayhook__
            except:
                pass    

        @classmethod
        def tearDown(cls):
            try :
                 sys.displayhook = iphook
            except:
                pass 
            
OPTIONFLAGS = (doctest.ELLIPSIS |
               doctest.NORMALIZE_WHITESPACE)

    
def test_suite():

    return unittest.TestSuite([
    

        # Integration tests
        ztc.FunctionalDocFileSuite(
            'readme.txt', package='collective.groupdelegation',
            optionflags=OPTIONFLAGS,
            test_class=TestCase),

        ])


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')

