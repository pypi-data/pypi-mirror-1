##############################################################################
#
# Copyright (c) 2006 Zope Corporation and Contributors.
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
"""Setup for zope.i18n package

$Id: setup.py 88152 2008-07-10 05:57:48Z srichter $
"""
import os
from setuptools import setup, find_packages

def read(*rnames):
    text = open(os.path.join(os.path.dirname(__file__), *rnames)).read()
    return text

setup(
    name='zope.i18n',
    version = '3.5.0',
    author='Zope Corporation and Contributors',
    author_email='zope3-dev@zope.org',
    description='Zope3 Internationalization Support',
    long_description=(
        read('README.txt')
        + '\n\n' +
        read('CHANGES.txt')
        ),
    license='ZPL 2.1',
    keywords=('zope3 internationalization localization i18n l10n '
              'gettext ICU locale'),
    classifiers = [
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Zope Public License',
        'Programming Language :: Python',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Topic :: Internet :: WWW/HTTP',
        'Framework :: Zope3'],
    url='http://cheeseshop.python.org/pypi/zope.i18n',
    packages=find_packages('src'),
    package_dir = {'': 'src'},
    namespace_packages=['zope',],
    install_requires=['setuptools',
                      'pytz',
                      'zope.i18nmessageid',
                      'zope.component [zcml]',
                      'zope.configuration',
                      ],
    include_package_data = True,
    zip_safe = False,
    extras_require = dict(
        compile = ['python-gettext'],
        ),
    )
