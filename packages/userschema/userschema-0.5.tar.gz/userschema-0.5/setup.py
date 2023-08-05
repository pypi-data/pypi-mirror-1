"""Setup for userschema package

$Id: setup.py,v 1.1 2006/09/19 20:42:36 tseaver Exp $
"""

import os

try:
    from setuptools import setup, Extension
except ImportError, e:
    from distutils.core import setup, Extension

setup(name='userschema',
      version='0.5',
      url='http://agendaless.com/home/tseaver/software/userschema',
      license='ZPL 2.1',
      description='Schema defined by business users',
      author='Tres Seaver, Agendaless Consulting, Inc.',
      author_email='tseaver@agendaless.com',
      long_description='Allow users to define schemas using CSV or HTML forms',
      packages=['userschema', 'userschema.tests'],
      package_dir = {'': 'src'},
      #namespace_packages=['zope',],
      #tests_require = ['zope_testing'],
      #devel_requires=[],
      include_package_data = True,
      #zip_safe = False,
      )

