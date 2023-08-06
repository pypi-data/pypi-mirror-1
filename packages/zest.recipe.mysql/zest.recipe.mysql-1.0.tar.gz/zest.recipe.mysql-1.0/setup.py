# -*- coding: utf-8 -*-
"""
This module contains the tool of zest.recipe.mysql
"""
import os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

version = '1.0'

long_description = (
    read('README.txt')
    + '\n\n' +
    read('CHANGES.txt')
    + '\n\n' +
    read('TODO.txt')
    + '\n\n' +
    #'Detailed Documentation\n'
    #'**********************\n'
    #+ '\n' +
    #read('zest', 'recipe', 'mysql', 'README.txt')
    #+ '\n\n' +
    read('CONTRIBUTORS.txt')
    )
entry_point = 'zest.recipe.mysql:Recipe'
entry_points = {"zc.buildout": ["default = %s" % entry_point]}

tests_require=['zope.testing', 'zc.buildout']

setup(name='zest.recipe.mysql',
      version=version,
      description="A Buildout recipe to setup a MySQL database.",
      long_description=long_description,
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        'Framework :: Buildout',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: Zope Public License',
        ],
      keywords='buildout recipe mysql',
      author='Jean-Paul Ladage',
      author_email='j.ladage@zestsoftware.nl',
      url='https://svn.zestsoftware.nl/svn/zest/zest.recipe.mysql/trunk',
      license='ZPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['zest', 'zest.recipe'],
      include_package_data=True,
      zip_safe=False,
      install_requires=['setuptools',
                        'zc.buildout'
                        # -*- Extra requirements: -*-
                        ],
      tests_require=tests_require,
      extras_require=dict(tests=tests_require),
      test_suite = 'zest.recipe.mysql.tests.test_docs.test_suite',
      entry_points=entry_points,
      )
