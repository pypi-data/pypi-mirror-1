##############################################################################
#
# Copyright (c) 2007 Zope Foundation and Contributors.
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
"""Setup

$Id: setup.py 97342 2009-02-27 10:54:10Z nadako $
"""
import os
import xml.sax.saxutils
from setuptools import setup, find_packages

def read(*rnames):
    text = open(os.path.join(os.path.dirname(__file__), *rnames)).read()
    return xml.sax.saxutils.escape(text)

setup (
    name='z3c.pagelet',
    version='1.0.3',
    author = "Roger Ineichen and the Zope Community",
    author_email = "zope-dev@zope.org",
    description = "Pagelets are way to specify a template without the O-wrap.",
    long_description=(
        read('README.txt')
        + '\n' +
        'Detailed Documentation\n'
        '**********************\n'
        + '\n' +
        read('src', 'z3c', 'pagelet', 'README.txt')
        + '\n' +
        read('CHANGES.txt')
        ),
    license = "ZPL 2.1",
    keywords = "zope3 template pagelet layout zpt pagetemplate",
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
    url = 'http://pypi.python.org/pypi/z3c.pagelet',
    packages = find_packages('src'),
    package_dir = {'':'src'},
    namespace_packages = ['z3c'],
    extras_require = dict(
        test = ['zope.app.testing',
                'zope.app.form',
                'zope.testing',
                'zope.traversing',
                'lxml>=2.1.1',
                'z3c.pt>=1.0b4',
                'z3c.ptcompat',
                ],
        docs = ['z3c.recipe.sphinxdoc'],
        ),
    install_requires = [
        'setuptools',
        'z3c.template>=1.2.0',
        'z3c.ptcompat',
        'zope.app.component', # TODO: these are only needed for ZCML directives, so can copy
        'zope.app.publisher', # things we use from there and get rid of the dependencies.
        'zope.component',
        'zope.configuration',
        'zope.contentprovider',
        'zope.formlib', # TODO: get rid of hard dependency on zope.formlib
        'zope.interface',
        'zope.publisher',
        'zope.schema',
        'zope.security',
        ],
    include_package_data = True,
    zip_safe = False,
    )
