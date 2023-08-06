# -*- coding: utf-8 -*-
"""
This module contains the tool of collective.simpleeditbutton
"""
import os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

version = '1.0'

long_description = (
    read('collective', 'simpleeditbutton', 'README.txt')
    + '\n' +
    'Change history\n'
    '**************\n'
    + '\n' +
    read('docs', 'HISTORY.txt')
    )

tests_require=['zope.testing']

setup(name='collective.simpleeditbutton',
      version=version,
      description="Adjusts the default permissions so that users with the Member role only "
                  "see an edit button for items they are allowed to modify, rather than the full "
                  "set of tabs and actions",
      long_description=long_description,
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        'Framework :: Plone',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        ],
      keywords='plone member edit',
      author='David Glick',
      author_email='davidglick@onenw.org',
      url='http://svn.plone.org/svn/collective/collective.simpleeditbutton',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective', ],
      include_package_data=True,
      zip_safe=False,
      install_requires=['setuptools',
                        'collective.autopermission',
                        # -*- Extra requirements: -*-
                        ],
      tests_require=tests_require,
      extras_require=dict(tests=tests_require),
      test_suite = 'collective.simpleeditbutton.tests.test_docs.test_suite',
      entry_points="""
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
