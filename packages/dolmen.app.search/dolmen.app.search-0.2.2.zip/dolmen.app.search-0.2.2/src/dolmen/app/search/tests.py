# -*- coding: utf-8 -*-

import os.path
import unittest

from zope.testing import module
from zope.app.testing import functional
from zope.security.testing import Principal, Participation
from zope.security.management import newInteraction, endInteraction

ftesting_zcml = os.path.join(os.path.dirname(__file__), 'ftesting.zcml')
FunctionalLayer = functional.ZCMLLayer(
    ftesting_zcml, __name__, 'FunctionalLayer', allow_teardown=True
    )


def setUp(test):
    module.setUp(test, 'dolmen.app.search.ftests')
    participation = Participation(Principal('zope.mgr'))
    newInteraction(participation)


def tearDown(test):
    module.tearDown(test)
    endInteraction()


def interfaceDescription(interface):
    for name, attr in interface.namesAndDescriptions():
        print "%s: %s" % (name, attr.getDoc())


def test_suite():
    suite = unittest.TestSuite()
    readme = functional.FunctionalDocFileSuite(
        'README.txt', setUp=setUp, tearDown=tearDown,
        globs={'interfaceDescription': interfaceDescription}
        )
    readme.layer = FunctionalLayer
    suite.addTest(readme)
    return suite
