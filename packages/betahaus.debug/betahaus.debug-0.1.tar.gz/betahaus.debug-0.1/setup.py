# -*- coding: utf-8 -*-
"""
This module contains the tool of betahaus.debug
"""
import os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

version = '0.1'

long_description = (
    read('README.txt')
    + '\n' +
    'Change history\n'
    '--------------\n'
    + '\n' +
    read('CHANGES.txt')
    + '\n' +
    'Contributors\n'
    '------------\n'
    + '\n' +
    read('CONTRIBUTORS.txt')

    )

tests_require=['zope.testing']

name = 'betahaus.debug'

setup(name=name,
      version=version,
      description="Simple debug help with pdb",
      long_description=long_description,
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        'Framework :: Plone',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        ],
      keywords='plone debug pdb',
      author='Martin Lundwall',
      author_email='martin@betahaus.net',
      url='http://pypi.python.org/pypi/' + name,
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['betahaus', ],
      include_package_data=True,
      zip_safe=False,
      install_requires=['setuptools',
                        ],
      tests_require=tests_require,
      extras_require=dict(tests=tests_require),
      test_suite = 'betahaus.debug.tests.test_docs.test_suite',
      entry_points="""
      # -*- entry_points -*- 
      """,
      )
