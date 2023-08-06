# -*- coding: utf-8 -*-
"""
This module contains the tool of twod.recipe.apacheconf
"""
import os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

version = '0.1'

long_description = (
    read('README.txt')
    + '\n' +
   'Download\n'
    '********\n'
    )

entry_point = 'twodeg.recipe.apacheconf.recipe:Recipe'
entry_points = {"zc.buildout": ["default = %s" % entry_point]}

dependencies = [ 'zc.recipe.egg', 'z3c.recipe.filetemplate']
tests_require=['zope.testing', 'zc.buildout', 'interlude'] + dependencies

setup(name='twodeg.recipe.apacheconf',
      version=version,
      description="An apache VirtualHost config generator",
      long_description=long_description,
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        'Framework :: Buildout',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        ],
      keywords='',
      author='Ben Ford',
      author_email='ben.fordnz@gmail.com',
      url='',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['twodeg', 'twodeg.recipe'],
      include_package_data=True,
      zip_safe=True,
      install_requires=['setuptools',
                        'zc.buildout',
                        # -*- Extra requirements: -*-
                       ] + dependencies,
      tests_require=tests_require,
      extras_require=dict(tests=tests_require),
      test_suite = 'twodeg.recipe.apacheconf.tests.test_docs.test_suite',
      entry_points=entry_points,
      )
