# -*- coding: utf-8 -*-
#
# Copyright 2006-2009, Blue Dynamics Alliance, Austria - www.bluedynamics.com
#
# GNU General Public Licence Version 2 or later - see LICENCE.GPL

__author__ = """Robert Niederreiter <rnix@squarewave.at>"""
__docformat__ = 'plaintext'

from setuptools import setup, find_packages
import sys, os

version = '1.1'

shortdesc = "Base common calendaring features: Convinience or not coverd yet."
longdesc = open(os.path.join(os.path.dirname(__file__), 'README.txt')).read()

setup(name='bda.calendar.base',
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
      ], # http://www.python.org/pypi?%3Aaction=list_classifiers
      keywords='Calendaring',
      author='Jens Klein, Robert Niedereiter',
      author_email='jens@bluedynamics.com, rnix@squarewave.at',
      url=u'https://svn.bluedynamics.net/svn/public/bda.calendar.base',
      license='General Public Licence',
      packages=find_packages('src'),
      package_dir = {'': 'src'},
      namespace_packages=['bda', 'bda.calendar'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'pytz',
          'zope.interface',              
          # -*- Extra requirements: -*
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )