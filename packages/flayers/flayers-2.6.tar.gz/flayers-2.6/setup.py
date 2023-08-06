#!/usr/bin/python
# -*- coding: utf-8 -*-
#  Copyright (C) 2001-2003, 2008-2009 Francis Piéraut <fpieraut@gmail.com>
#  Copyright (C) 2009 Yannick Gingras <ygingras@ygingras.net>

#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Affero General Public License as
#  published by the Free Software Foundation, either version 3 of the
#  License, or (at your option) any later version.

#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Affero General Public License for more details.

#  You should have received a copy of the GNU Affero General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.

''' Installer for the `flayers` python API wrapper.  To install, run:  
  python setup.py build_ext --inplace or python setup.py install'''

# from distutils.core import setup, Extension
from setuptools import setup, Extension
from setuptools import find_packages
from subprocess import call
import os

import sys
sys.path.append("flayers")
from metainfos import __version__, FLAYERS_CORE_FILES

flayers_modules_files = [os.path.join("flayers", "src", f) 
                         for f in FLAYERS_CORE_FILES]
# To create flayers_wrap.cxx you have to call swig like that: swig -python -c++ flayers.i
for filename in ['flayers/flayers']:
    print "creating %s_wrap.cxx" % filename
    call(['swig', '-python', '-c++', '%s.i' % filename])
    flayers_modules_files.extend(['%s.cpp' % filename, '%s_wrap.cxx' % filename]) 

flayers_extension = Extension("_flayers", sources=flayers_modules_files)

setup(name='flayers',
      version=__version__,
      author='Francis Pieraut',
      author_email='fpieraut@gmail.com',
      description = "python flayers wrapper interface",
      license="AGPL v3 or later",
      url='http://sourceforge.net/projects/mlboost/',
      packages = find_packages(),
      ext_modules = [flayers_extension],
      include_package_data=True,
      #setup_requires = ['swig>1.3.35']
)
