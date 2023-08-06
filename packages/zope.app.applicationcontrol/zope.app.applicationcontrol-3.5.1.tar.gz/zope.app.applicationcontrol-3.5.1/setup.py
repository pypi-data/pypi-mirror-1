##############################################################################
#
# Copyright (c) Zope Foundation and Contributors.
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
version = '3.5.1'

import os

from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

setup(name='zope.app.applicationcontrol',
    version = version,
    author='Zope Corporation and Contributors',
    author_email='zope3-dev@zope.org',
    description='Zope applicationcontrol',
    long_description=(
        read('README.txt')
        + '\n\n' +
        read('INSTALL.txt')
        + '\n\n' +
        read('CHANGES.txt')
        ),
    license='ZPL 2.1',
    keywords = "zope3 application control",
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
    url='http://cheeseshop.python.org/pypi/zope.app.applicationcontrol',
    extras_require=dict(
        test=['zope.app.authentication',
              'zope.app.component',
              'zope.app.securitypolicy',
              'zope.app.testing',
              'zope.app.zcmlfiles',
              'zope.app.zptpage',
              'zope.testbrowser',
              ]),
    package_dir = {'': 'src'},
    packages=find_packages('src'),
    namespace_packages=['zope', 'zope.app'],
    install_requires=[
          'setuptools',
          'zope.app.appsetup',
          'zope.error',
          'zope.i18n',
          'zope.interface',
          'zope.size',
          'zope.traversing>=3.7.0',
        ],
    include_package_data = True,
    zip_safe = False,
    )
