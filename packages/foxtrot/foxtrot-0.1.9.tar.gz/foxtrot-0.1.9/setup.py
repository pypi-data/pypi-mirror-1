#!/usr/bin/env python
# -*- coding: UTF-8 -*-
###############################################################################                                       
# Name: setup.py                                                              #                                       
# Description: Setup script for foxtrot package                               #                                       
# Author: Alexey Zankevich <alex.zankevich@gmail.com>                         #                                       
# Copyright: (c) 2009 Alexey Zankevich <alex.zankevich@gmail.com>             #                                       
# Licence: GPLv3                                                              #                                       
###############################################################################                                       
__version__ = "0.1"
__author__ = "Alexey Zankevich <alex.zankevich@gmail.com>"
__copyright__ = "Copyright: (c) 2009 Alexey Zankevich <alex.zankevich@gmail.com>"
__license__ = "GPLv3"


from distutils.core import setup


setup(name='foxtrot',
      version='0.1.9',
      description='Package for Python code analyzing',
      author='Alexey Zankevich',
      author_email='alex.zankevich@gmail.com', 
      packages=['foxtrot']
      )
