#!/usr/bin/env python
# -*- coding: utf-8 -*-

#***************************************************************************
#*   Copyright (C) 2009 by Steve Walter, Oliver Borm                       *
#*   steve.walter@mytum.de, oli.borm@web.de                                *
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

# Author: Steve Walter, Oliver Borm
# Date: March 2009

from distutils.core import setup, Extension
import distutils.sysconfig

Version = "0.3"

setup(
	name='PythonNURBS',
	version=Version,
	description='PythonNURBS is the Python language binding for the NURBS++ library.',
	author='Steve Walter',
	author_email='steve.walter@mytum.de',
	maintainer='Oliver Borm',
	maintainer_email='oli.borm@web.de',
	url='http://pypi.python.org/pypi/PythonNURBS',
	license='GPL-3',
	packages=['pythonnurbs'],
	ext_package='pythonnurbs',
	package_dir={'pythonnurbs':'src'},
	package_data={'pythonnurbs':['src/__init__.py']},
	ext_modules =	[ Extension("_NurbsColor", ["src/color.i"], libraries=["nurbsd", "matrixN", "matrixI", "matrix"], swig_opts=["-c++", "-I/usr/include"]),
	 		Extension("_NurbsCurve", ["src/curve.i"], libraries=["nurbsd", "matrixN", "matrixI", "matrix"], swig_opts=["-c++", "-I/usr/include"]),
			Extension("_NurbsMatrix", ["src/matrix.i"], libraries=["nurbsd", "matrixN", "matrixI", "matrix"], swig_opts=["-c++", "-I/usr/include"]),
			Extension("_NurbsBasicArray", ["src/barray.i"], libraries=["nurbsd", "matrixN", "matrixI", "matrix"], swig_opts=["-c++", "-I/usr/include"]),
			Extension("_NurbsArray2D", ["src/barray2d.i"], libraries=["nurbsd", "matrixN", "matrixI", "matrix"], swig_opts=["-c++", "-I/usr/include"]),
			Extension("_NurbsCoordinate", ["src/coordinate.i"], libraries=["nurbsd", "matrixN", "matrixI", "matrix"], swig_opts=["-c++", "-I/usr/include"]),
			Extension("_NurbsHPoint", ["src/hpoint_nd.i"], libraries=["nurbsd", "matrixN", "matrixI", "matrix"], swig_opts=["-c++", "-I/usr/include"]),
			Extension("_NurbsPoint", ["src/point_nd.i"],  libraries=["nurbsd", "matrixN", "matrixI", "matrix"], swig_opts=["-c++", "-I/usr/include"]),
			Extension("_NurbsBasicList", ["src/list.i"],  libraries=["nurbsd", "matrixN", "matrixI", "matrix"], swig_opts=["-c++", "-I/usr/include"]),
		 	Extension("_NurbsSurface", ["src/surface.i"],  libraries=["nurbsd", "matrixN", "matrixI", "matrix"], swig_opts=["-c++", "-I/usr/include"]),
			Extension("_NurbsVector", ["src/vector.i"],  libraries=["nurbsd", "matrixN", "matrixI", "matrix"], swig_opts=["-c++", "-I/usr/include"]),
			Extension("_NurbsMatrixRT", ["src/matrixRT.i"], libraries=["nurbsd", "matrixN", "matrixI", "matrix"], swig_opts=["-c++", "-I/usr/include"])],
	data_files =	[('share/doc/pythonnurbs-'+Version+'/examples', ['examples/curve01.py', 'examples/interpolation01.py',
			'examples/interpolation02.py', 'examples/surface01.py', 'examples/surface02.py', 'examples/test.py',
			'examples/vector_double.py']),
			( distutils.sysconfig.get_python_lib() + '/pythonnurbs',['src/NurbsColor.py', 'src/NurbsCurve.py', 'src/NurbsMatrix.py', 'src/NurbsBasicArray.py', 'src/NurbsArray2D.py', 'src/NurbsCoordinate.py', 'src/NurbsHPoint.py', 'src/NurbsPoint.py', 'src/NurbsBasicList.py', 'src/NurbsSurface.py', 'src/NurbsVector.py', 'src/NurbsMatrixRT.py'])],
	classifiers=	['Development Status :: 3 - Alpha',
			'Intended Audience :: Science/Research',
			'Intended Audience :: Developers',
			'License :: OSI Approved :: GNU General Public License (GPL)',
			'Topic :: Scientific/Engineering :: Physics']
      )
