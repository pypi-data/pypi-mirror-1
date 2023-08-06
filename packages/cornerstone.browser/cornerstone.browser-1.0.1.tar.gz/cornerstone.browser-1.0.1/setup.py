#
# Copyright 2008, Blue Dynamics Alliance, Austria - http://bluedynamics.com
#
# GNU General Public Licence Version 2 or later

__author__ = """Robert Niederreiter <rnix@squarewave.at>"""
__docformat__ = 'plaintext'

from setuptools import setup, find_packages
import sys, os

version = '1.0.1'
shortdesc = "Common browser utils"
longdesc = open(os.path.join(os.path.dirname(__file__), 'README.txt')).read()

setup(name='cornerstone.browser',
      version=version,
      description=shortdesc,
      long_description=longdesc,
      classifiers=[
            'Development Status :: 4 - Beta',
            'Environment :: Web Environment',
            'Framework :: Zope2',
            'License :: OSI Approved :: GNU General Public License (GPL)',
            'Operating System :: OS Independent',
            'Programming Language :: Python',
            'Topic :: Internet :: WWW/HTTP :: Dynamic Content',            
      ], # Get strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      keywords='',
      author='Robert Niedereiter',
      author_email='rnix@squarewave.at',
      url='https://svn.plone.org/svn/collective/cornerstone.browser',
      license='General Public Licence',
      packages=find_packages(exclude=['ez_setup',]),
      namespace_packages=['cornerstone'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',                        
          # -*- Extra requirements: -*
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )

