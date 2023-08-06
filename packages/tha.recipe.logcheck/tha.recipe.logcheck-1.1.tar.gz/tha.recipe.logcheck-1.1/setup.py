# -*- coding: utf-8 -*-
"""
This module contains the tool of tha.recipe.logcheck
"""
import os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(*rnames)).read()

version = '1.1'

long_description = (
    read('README.txt')
    + '\n\n' +
    read('src', 'tha', 'recipe', 'logcheck', 'README.txt')
    + '\n\n' +
    read('CONTRIBUTORS.txt')
    + '\n\n' +
    read('CHANGES.txt')
    )
entry_point = 'tha.recipe.logcheck:Recipe'
entry_points = {"zc.buildout": ["default = %s" % entry_point]}

tests_require=['zope.testing', 'zc.buildout', 'zc.recipe.egg',
               'z3c.recipe.usercrontab']

setup(name='tha.recipe.logcheck',
      version=version,
      description="Logcheck configuration recipe",
      long_description=long_description,
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        'Framework :: Buildout',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: Zope Public License',
        ],
      keywords='',
      author='The Health Agency',
      author_email='techniek@thehealthagency.com',
      url='http://pypi.python.org/pypi/tha.recipe.logcheck',
      license='BSD',
      package_dir={'': 'src'},
      packages=find_packages('src'),
      namespace_packages=['tha', 'tha.recipe'],
      include_package_data=True,
      zip_safe=False,
      install_requires=['setuptools',
                        'zc.buildout',
                        # -*- Extra requirements: -*-
                        'zc.recipe.egg',
                        ],
      tests_require=tests_require,
      extras_require=dict(tests=tests_require),
      test_suite = 'tha.recipe.logcheck.tests.test_docs.test_suite',
      entry_points=entry_points,
      )
