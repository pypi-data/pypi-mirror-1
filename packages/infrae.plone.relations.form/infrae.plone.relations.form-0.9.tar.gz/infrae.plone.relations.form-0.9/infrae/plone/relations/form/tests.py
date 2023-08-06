# -*- coding: utf-8 -*-
# Copyright (c) 2007-2008 Infrae. All rights reserved.
# $Id: tests.py 29164 2008-06-12 13:02:07Z sylvain $

__author__ ="sylvain@infrae.com"
__format__ ="plaintext"
__version__ ="$Id: tests.py 29164 2008-06-12 13:02:07Z sylvain $"

import unittest
from zope.testing import doctest

from Testing.ZopeTestCase import FunctionalDocFileSuite
from Products.PloneTestCase import ptc

from five.intid.site import add_intids
from plone.app.relations.utils import add_relations
from five.intid.lsm import USE_LSM

from Products.Five import zcml

class TestCase(ptc.FunctionalTestCase):

    def afterSetUp(self):

        from infrae.plone.relations import form
        zcml.load_config('configure.zcml', form)

        if not USE_LSM:
            # monkey in our hooks
            from Products.Five.site.metaconfigure import classSiteHook
            from Products.Five.site.localsite import FiveSite
            from zope.interface import classImplements
            from zope.app.component.interfaces import IPossibleSite
            klass = self.portal.__class__
            classSiteHook(klass, FiveSite)
            classImplements(klass, IPossibleSite)
            
        add_intids(self.portal)
        add_relations(self.portal)



OPTIONS = doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE

def test_suite():
    

    ptc.setupPloneSite(),
    
    return unittest.TestSuite((
        FunctionalDocFileSuite('README.txt',
                               test_class=TestCase,
                               optionflags=OPTIONS,
                               ),
        FunctionalDocFileSuite('README.EXT.txt',
                               test_class=TestCase,
                               optionflags=OPTIONS,
                               ),
        ))




if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
