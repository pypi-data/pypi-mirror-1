# -*- coding: utf-8 -*-
"""
This module contains the tool of quintagroup.doublecolumndocument
"""
import os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

version = '0.2'

tests_require=['zope.testing']

setup(name='quintagroup.doublecolumndocument',
      version=version,
      description="Extends Document with one more extra column",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        'Framework :: Plone',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        ],
      keywords='plone content archetypes document doublecolumn',
      author='(c) "Quintagroup"',
      author_email='support@quintagroup.com',
      url='http://quintagroup.com/services/plone-development/products/',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['quintagroup', ],
      include_package_data=True,
      zip_safe=False,
      install_requires=['setuptools',
                        # -*- Extra requirements: -*-
                        ],
      tests_require=tests_require,
      extras_require=dict(tests=tests_require),
      test_suite = 'quintagroup.doublecolumndocument.tests.test_docs.test_suite',
      entry_points="""
      # -*- entry_points -*- 
      """,
      )
