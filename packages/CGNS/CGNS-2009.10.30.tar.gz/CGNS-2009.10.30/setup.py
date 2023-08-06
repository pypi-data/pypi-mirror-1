#!/usr/bin/env python
# -*- coding: utf-8 -*-

#***************************************************************************
#*   Copyright (C) 2009 by Steve Walter, Oliver Borm, Franz Blaim          *
#*   steve.walter@mytum.de, oli.borm@web.de, franz.blaim@gmx.de            *
#*                                                                         *
#*   This program is free software; you can redistribute it and/or modify  *
#*   it under the terms of the GNU General Public License as published by  *
#*   the Free Software Foundation; either version 3 of the License, or     *
#*   (at your option) any later version.                                   *
#*                                                                         *
#*   This program is distributed in the hope that it will be useful,       *
#*   but WITHOUT ANY WARRANTY; without even the implied warranty of        *
#*   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         *
#*   GNU General Public License for more details.                          *
#*                                                                         *
#*   You should have received a copy of the GNU General Public License     *
#*   along with this program; if not, write to the                         *
#*   Free Software Foundation, Inc.,                                       *
#*   59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.             *
#***************************************************************************

# Author: Steve Walter, Franz Blaim, Oliver Borm
# Date: March 2009

from distutils.core import setup, Extension
import distutils.sysconfig

setup(
	name='CGNS',
	version='2009.10.30',
	description='Pythonbindings for CGNS library',
	author='Steve Walter',
	author_email='steve.walter@mytum.de',
	maintainer='Oliver Borm',
	maintainer_email='oli.borm@web.de',
	url='http://pypi.python.org/pypi/PythonNURBS',
	license='GPL-3',
	packages=['CGNS'],
	ext_package='CGNS',
	package_dir={'CGNS':'src'},
	package_data={'CGNS':['src/__init__.py']},
	ext_modules =	[ Extension("_CGNS", ["src/cgnslib.i"], libraries=["cgns"],swig_opts=["-I/usr/include"])],
	data_files = [('share/doc/pythoncgns-0.1/examples', ['tutorial/cgnsTest.py']),
	 		(distutils.sysconfig.get_python_lib() + '/CGNS', ['src/CGNS.py'])],
	classifiers=	['Development Status :: 3 - Alpha',
			'Intended Audience :: Science/Research',
			'Intended Audience :: Developers',
			'License :: OSI Approved :: GNU General Public License (GPL)',
			'Topic :: Scientific/Engineering :: Physics']
      )
