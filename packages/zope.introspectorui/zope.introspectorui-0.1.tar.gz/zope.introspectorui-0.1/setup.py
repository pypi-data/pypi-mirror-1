##############################################################################
#
# Copyright (c) 2008 Zope Corporation and Contributors.
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
"""Setup for zope.introspectorui package

$Id: setup.py 92524 2008-10-24 08:30:43Z mlundwall $
"""
import os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

version = '0.1'
name='zope.introspectorui'

long_description = (
    read('README.txt')
    + '\n' +
    read('CHANGES.txt')
    )

setup(name=name,
      version=version,
      description="Views for the info objects from zope.introspector.",
      long_description=long_description,
      # Get strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Zope Public License',
        'Programming Language :: Python',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Topic :: Internet :: WWW/HTTP',
        'Framework :: Zope3',
        ],
      keywords="zope zope2 zope3 web introspection introspector",
      author="Zope Corporation and Contributors",
      author_email="zope3-dev@zope.org",
      url='http://pypi.python.org/pypi/'+name,
      license="ZPL 2.1",
      package_dir={'': 'src'},
      packages=find_packages('src'),
      namespace_packages = ['zope'],
      include_package_data=True,
      zip_safe=False,
      install_requires=['setuptools',
                        'grokcore.component',
                        'grokcore.view',
                        'zope.interface',
                        'zope.component',
                        'zope.introspector',
                        'z3c.autoinclude',
                        ],
      extras_require = dict(
        test=['zope.app.testing',
              'zope.testing',
              'z3c.testsetup',
              'zope.securitypolicy',
              ]
      ),
      entry_points="""
      # Add entry points here
      """,
      )
