"""Setup for userschema package

$Id: setup.py,v 1.5 2007/02/12 12:42:50 tseaver Exp $
"""

import os

try:
    from setuptools import setup, Extension
except ImportError, e:
    from distutils.core import setup, Extension

setup(name='userschema',
      version='0.7.2',
      url='http://agendaless.com/Members/tseaver/software/userschema',
      license='ZPL 2.1',
      description='Schema defined by business users',
      author='Tres Seaver, Agendaless Consulting, Inc.',
      author_email='tseaver@agendaless.com',
      long_description='Allow users to define schemas using CSV or HTML forms',
      platform='Any',
      packages=['userschema', 'userschema.tests'],
      package_dir = {'': 'src'},
      package_data = {'': ['*.txt', '*.zcml']},
      install_requires=['elementtree',
                        'zope.configuration',
                        'zope.i18nmessageid',
                        'zope.interface',
                        'zope.schema',
                       ],
      include_package_data = True,
      zip_safe = False,
      )

