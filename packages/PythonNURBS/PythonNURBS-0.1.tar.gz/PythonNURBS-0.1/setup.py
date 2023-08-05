#!/usr/bin/env python
# -*- coding: utf-8 -*-

#***************************************************************************
#*   Copyright (C) 2008-2008 by Oliver Borm                                *
#*   oli.borm@web.de                                                       *
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

# Author: Oliver Borm
# Date: February 2008

from distutils.core import setup, Extension

setup(
	name='PythonNURBS',
	version='0.1',
	description='PythonNURBS is the Python language binding for the NURBS++ library.',
	author='Franz Blaim',
	author_email='franz.blaim@gmx.de',
	maintainer='Oliver Borm',
	maintainer_email='oli.borm@web.de',
	url='http://pypi.python.org/pypi/PythonNURBS',
	ext_modules =	[Extension("NurbsColor", ["src/NurbsColor.cpp"], extra_compile_args=["-O2"],
			libraries=["boost_python", "nurbsd", "matrixN", "matrixI", "matrix"]),
	 		Extension("NurbsCurveD", ["src/NurbsCurveD.cpp"], extra_compile_args=["-O2"],
			libraries=["boost_python", "nurbsd", "matrixN", "matrixI", "matrix"]),
			Extension("NurbsMatrixD", ["src/NurbsMatrixD.cpp"], extra_compile_args=["-O2"],
			libraries=["boost_python", "nurbsd", "matrixN", "matrixI", "matrix"]),
			Extension("NurbsMatrixRTD", ["src/NurbsMatrixRTD.cpp"], extra_compile_args=["-O2"],
			libraries=["boost_python", "nurbsd", "matrixN", "matrixI", "matrix"]),
			Extension("NurbsPointD", ["src/NurbsPointD.cpp"], extra_compile_args=["-O2"],
			libraries=["boost_python", "nurbsd", "matrixN", "matrixI", "matrix"]),
			Extension("NurbsHPointD", ["src/NurbsHPointD.cpp"], extra_compile_args=["-O2"],
			libraries=["boost_python", "nurbsd", "matrixN", "matrixI", "matrix"]),
			Extension("NurbsSurfaceD", ["src/NurbsSurfaceD.cpp"], extra_compile_args=["-O2"],
			libraries=["boost_python", "nurbsd", "matrixN", "matrixI", "matrix"]),
			Extension("NurbsVectorD", ["src/NurbsVectorD.cpp"], extra_compile_args=["-O2"],
			libraries=["boost_python", "nurbsd", "matrixN", "matrixI", "matrix"])],
	data_files=[('share/doc/pythonnurbs-0.1/examples', ['examples/curve01.py', 'examples/interpolation01.py', 'examples/surface01.py', 'examples/test.py'])],
	classifiers=	['Development Status :: 3 - Alpha',
			'Environment :: Console',
			'Intended Audience :: Science/Research',
			'Intended Audience :: Developers',
			'License :: OSI Approved :: GNU General Public License (GPL)',
			'Operating System :: POSIX',
			'Programming Language :: C++',
			'Topic :: Scientific/Engineering :: Visualization',
			'Topic :: Scientific/Engineering :: Mathematics']
	)
