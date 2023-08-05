##############################################################################
#
# Copyright (c) 2006 Agendaless Consulting.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Setup for pushpage package

$Id: setup.py,v 1.3 2006/10/05 20:25:36 tseaver Exp $
"""

import os

try:
    from setuptools import setup
except ImportError, e:
    from distutils.core import setup

setup(name='pushpage',
      version='0.3',
      url='http://agendaless.com/Members/tseaver/software/pushpage',
      license='ZPL 2.1',
      description='Push-mode ZPT pages',
      author='Tres Seaver, Agendaless Consulting',
      author_email='tseaver@agendaless.com',
      long_description='"Push"-mode is jargon used in a number of templating '
                        'systems to describe templates which have their data '
                        '"pushed" to them as a mapping, supplied by the '
                        'application.  Tradiional ZPT contexts include '
                        'top-level variables (e.g., "context") from which the '
                        'template "pulls" data.  This package offers a variant '
                        'of ZPT which suppresses any context variables except '
                        'those explicitly passed by the caller. ',

      packages=['pushpage', 'pushpage.tests'],
      
      install_requires=['zope.pagetemplate'],
      include_package_data = True,

      zip_safe = False,
      )
