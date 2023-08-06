#
# Copyright 2008-2009, Blue Dynamics Alliance, Austria - http://bluedynamics.com
#
# GNU General Public Licence Version 2 or later

__author__ = """Robert Niederreiter <rnix@squarewave.at>"""
__docformat__ = 'plaintext'

from setuptools import setup, find_packages
import sys, os

version = '1.3.1'
shortdesc ="Archetypes Datetime Widget using bda.intellidatetime conversion"
longdesc = open(os.path.join(os.path.dirname(__file__), 'README.txt')).read()
changes = open(os.path.join(os.path.dirname(__file__), 'CHANGES.txt')).read()

setup(name='Products.IntelliDateTime',
      version=version,
      description=shortdesc,
      long_description=longdesc + changes,
      classifiers=[
            'Development Status :: 5 - Production/Stable',
            'Environment :: Web Environment',
            'Framework :: Zope2',
            'License :: OSI Approved :: GNU General Public License (GPL)',
            'Operating System :: OS Independent',
            'Programming Language :: Python', 
            'Topic :: Internet :: WWW/HTTP :: Dynamic Content',        
      ], # http://www.python.org/pypi?%3Aaction=list_classifiers
      keywords='',
      author='Robert Niederreiter',
      author_email='rnix@squarewave.at',
      url=u'https://svn.plone.org/svn/archetypes/MoreFieldsAndWidgets/IntelliDateTime',
      license='General Public Licence',
      packages=find_packages('src'),
      package_dir = {'': 'src'},
      namespace_packages=['Products'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools', 
          'bda.intellidatetime',
          'bda.calendar.base',
          'van.timeformat',
          # -*- Extra requirements: -*
      ],
      extras_require={
      },
      entry_points="""
      # -*- Entry points: -*-
      """,
      )