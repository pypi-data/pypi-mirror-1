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

$Id: setup.py 80755 2007-10-10 01:57:53Z srichter $
"""
import os
import xml.sax.saxutils
from setuptools import setup, find_packages

def read(*rnames):
    text = open(os.path.join(os.path.dirname(__file__), *rnames)).read()
    return xml.sax.saxutils.escape(text)

chapters = '\n'.join(
    [read('src', 'z3c', 'form', name)
    for name in ('README.txt',
                 'form.txt',
                 'group.txt',
                 'subform.txt',
                 'field.txt',
                 'button.txt',
                 'zcml.txt',
                 'validator.txt',
                 'widget.txt',
                 'action.txt',
                 'value.txt',
                 'datamanager.txt',
                 'converter.txt',
                 'term.txt',
                 'util.txt')])

setup (
    name='z3c.form',
    version='1.7.0',
    author = "Stephan Richter, Roger Ineichen and the Zope Community",
    author_email = "zope3-dev@zope.org",
    description = "An advanced form and widget framework for Zope 3",
    long_description=(
        read('README.txt')
        + '\n\n' +
        'Detailed Documentation\n'
        '**********************\n'
        + '\n' + chapters
        + '\n\n' +
        read('CHANGES.txt')
        ),
    license = "ZPL 2.1",
    keywords = "zope3 form widget",
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
    url = 'http://cheeseshop.python.org/pypi/z3c.form',
    packages = find_packages('src'),
    include_package_data = True,
    package_dir = {'':'src'},
    namespace_packages = ['z3c'],
    extras_require = dict(
        test = ['zope.app.container', 'zope.testing',
                'z3c.coverage', 'z3c.template'],
        adding = ['zope.app.container'],
        ),
    install_requires = [
        'setuptools',
        'zope.app.pagetemplate',
        'zope.app.testing',
        'zope.component',
        'zope.configuration',
        'zope.event',
        'zope.i18n',
        'zope.i18nmessageid',
        'zope.interface',
        'zope.lifecycleevent',
        'zope.location',
        'zope.pagetemplate',
        'zope.publisher',
        'zope.schema',
        'zope.security',
        ],
    dependency_links = ['http://download.zope.org/distribution'],
    zip_safe = False,
    )
