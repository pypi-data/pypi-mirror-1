# -*- coding: utf-8 -*-
"""
This module contains the tool of fez.atcsv
"""
import os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

version = '0.2'

long_description = '\n'.join([
    read('README.rst') ,
    read('docs/HISTORY.rst'), 
    read('fez', 'atcsv', 'README.rst'),
    read('CONTRIBUTORS.rst'),
    ])

tests_require=['zope.testing']

setup(name='fez.atcsv',
      version=version,
      description="Simple AT CSV processing",
      long_description=long_description,
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        'Framework :: Plone',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: BSD License',
        'Development Status :: 3 - Alpha',
        ],
      keywords='plone zope archetypes csv import',
      author='Dan Fairs',
      author_email='dan@fezconsulting.com',
      url='http://www.fezconsulting.com',
      license='BSD',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['fez', ],
      include_package_data=True,
      zip_safe=False,
      install_requires=['setuptools',
                        'plone.app.z3cform',
                        ],
      tests_require=tests_require,
      extras_require=dict(tests=tests_require),
      test_suite = 'fez.atcsv.tests.test_suite',
      entry_points="""
      # -*- entry_points -*- 
      [distutils.setup_keywords]
      paster_plugins = setuptools.dist:assert_string_list

      [egg_info.writers]
      paster_plugins.txt = setuptools.command.egg_info:write_arg
      """,
      paster_plugins = ["ZopeSkel"],
      )
