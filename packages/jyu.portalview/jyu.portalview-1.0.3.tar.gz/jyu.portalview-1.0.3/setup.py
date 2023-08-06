# -*- coding: utf-8 -*-
"""
This module contains the tool of jyu.portalview
"""
import os
from setuptools import setup, find_packages

long_description = (
    '.. contents::\n\n'
    + open('README.txt').read()
    + '\n\n'
    + open(os.path.join('jyu', 'portalview', 'README.txt')).read()
    + '\n\n'
    + open('CHANGES.txt').read()
    )

version = '1.0.3'

setup(name='jyu.portalview',
      version=version,
      description="A content type, which displays content in a portal like aggregating view",
      long_description=long_description,
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        'Framework :: Plone',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        ],
      keywords='plone content portal view',
      author='Jukka Ojaniemi',
      author_email='jukka.ojaniemi@jyu.fi',
      url='http://svn.plone.org/svn/collective/jyu.portalview',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['jyu', ],
      include_package_data=True,
      zip_safe=False,
      install_requires=['setuptools',
                        # -*- Extra requirements: -*-
                        ],
      entry_points="""
      # -*- entry_points -*- 
      """,
      )