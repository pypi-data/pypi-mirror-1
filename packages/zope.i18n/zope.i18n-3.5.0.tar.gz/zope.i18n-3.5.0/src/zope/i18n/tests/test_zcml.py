##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
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
"""Test the gts ZCML namespace directives.

$Id: test_zcml.py 88073 2008-07-06 17:28:53Z hannosch $
"""
import os
import shutil
import unittest

from zope.component import getUtility
from zope.component import queryUtility
from zope.component.testing import PlacelessSetup
from zope.configuration import xmlconfig

import zope.i18n.tests
from zope.i18n.interfaces import ITranslationDomain
from zope.i18n.compile import HAS_PYTHON_GETTEXT
from zope.i18n import config
from zope.i18n import zcml

template = """\
<configure
    xmlns='http://namespaces.zope.org/zope'
    xmlns:i18n='http://namespaces.zope.org/i18n'>
  %s
</configure>"""

class DirectivesTest(PlacelessSetup, unittest.TestCase):

    def setUp(self):
        super(DirectivesTest, self).setUp()
        self.context = xmlconfig.file('meta.zcml', zope.i18n)
        self.allowed = config.ALLOWED_LANGUAGES
        config.ALLOWED_LANGUAGES = None

    def tearDown(self):
        super(DirectivesTest, self).tearDown()
        config.ALLOWED_LANGUAGES = self.allowed

    def testRegisterTranslations(self):
        self.assert_(queryUtility(ITranslationDomain) is None)
        xmlconfig.string(
            template % '''
            <configure package="zope.i18n.tests">
            <i18n:registerTranslations directory="locale" />
            </configure>
            ''', self.context)
        path = os.path.join(os.path.dirname(zope.i18n.tests.__file__),
                            'locale', 'en', 'LC_MESSAGES', 'zope-i18n.mo')
        util = getUtility(ITranslationDomain, 'zope-i18n')
        self.assertEquals(util._catalogs.get('test'), ['test'])
        self.assertEquals(util._catalogs.get('en'), [unicode(path)])

    def testAllowedTranslations(self):
        self.assert_(queryUtility(ITranslationDomain) is None)
        config.ALLOWED_LANGUAGES = ('de', 'fr')
        xmlconfig.string(
            template % '''
            <configure package="zope.i18n.tests">
            <i18n:registerTranslations directory="locale" />
            </configure>
            ''', self.context)
        path = os.path.join(os.path.dirname(zope.i18n.tests.__file__),
                            'locale', 'de', 'LC_MESSAGES', 'zope-i18n.mo')
        util = getUtility(ITranslationDomain, 'zope-i18n')
        self.assertEquals(util._catalogs,
                          {'test': ['test'], 'de': [unicode(path)]})

    def testRegisterDistributedTranslations(self):
        self.assert_(queryUtility(ITranslationDomain) is None)
        xmlconfig.string(
            template % '''
            <configure package="zope.i18n.tests">
            <i18n:registerTranslations directory="locale" />
            </configure>
            ''', self.context)
        xmlconfig.string(
            template % '''
            <configure package="zope.i18n.tests">
            <i18n:registerTranslations directory="locale2" />
            </configure>
            ''', self.context)
        path1 = os.path.join(os.path.dirname(zope.i18n.tests.__file__),
                             'locale', 'en', 'LC_MESSAGES', 'zope-i18n.mo')
        path2 = os.path.join(os.path.dirname(zope.i18n.tests.__file__),
                             'locale2', 'en', 'LC_MESSAGES', 'zope-i18n.mo')
        util = getUtility(ITranslationDomain, 'zope-i18n')
        self.assertEquals(util._catalogs.get('test'), ['test', 'test'])
        self.assertEquals(util._catalogs.get('en'),
                          [unicode(path1), unicode(path2)])

        msg = util.translate(u'Additional message', target_language='en')
        self.assertEquals(msg, u'Additional message translated')

        msg = util.translate(u'New Domain', target_language='en')
        self.assertEquals(msg, u'New Domain translated')

        msg = util.translate(u'New Language', target_language='en')
        self.assertEquals(msg, u'New Language translated')

    if HAS_PYTHON_GETTEXT:
        def testRegisterAndCompileTranslations(self):
            config.COMPILE_MO_FILES = True
            self.assert_(queryUtility(ITranslationDomain) is None)

            # Copy an old and outdated file over, so we can test if the
            # newer file check works
            testpath = os.path.join(os.path.dirname(zope.i18n.tests.__file__))
            basepath = os.path.join(testpath, 'locale3', 'en', 'LC_MESSAGES')
            in_ = os.path.join(basepath, 'zope-i18n.in')
            path = os.path.join(basepath, 'zope-i18n.mo')
            shutil.copy2(in_, path)

            xmlconfig.string(
                template % '''
                <configure package="zope.i18n.tests">
                <i18n:registerTranslations directory="locale3" />
                </configure>
                ''', self.context)
            util = getUtility(ITranslationDomain, 'zope-i18n')
            self.assertEquals(util._catalogs,
                              {'test': ['test'], 'en': [unicode(path)]})

            msg = util.translate(u"I'm a newer file", target_language='en')
            self.assertEquals(msg, u"I'm a newer file translated")

            util = getUtility(ITranslationDomain, 'zope-i18n2')
            msg = util.translate(u"I'm a new file", target_language='en')
            self.assertEquals(msg, u"I'm a new file translated")


def test_suite():
    return unittest.makeSuite(DirectivesTest)

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
