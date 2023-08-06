/***************************************************************************
*   Copyright (C) 2009 by Steve Walter, Oliver Borm                       *
*   steve.walter@mytum.de, oli.borm@web.de                                *
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU General Public License as published by  *
*   the Free Software Foundation; either version 3 of the License, or     *
*   (at your option) any later version.                                   *
*                                                                         *
*   This program is distributed in the hope that it will be useful,       *
*   but WITHOUT ANY WARRANTY; without even the implied warranty of        *
*   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         *
*   GNU General Public License for more details.                          *
*                                                                         *
*   You should have received a copy of the GNU General Public License     *
*   along with this program; if not, write to the                         *
*   Free Software Foundation, Inc.,                                       *
*   59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.             *
***************************************************************************

Author: Steve Walter, Oliver Borm
Date: March 2009
*/

%module NurbsMatrix
%{
#include <nurbs++/matrix.h>
%}

%import General.i
%import barray2d.i
%import point_nd.i
%import hpoint_nd.i
%import vector.i

%ignore operator!=;

%ignore operator*;

%rename(as_func) PLib::Matrix::as;

%include nurbs++/matrix.h

%template(Matrix_double) PLib::Matrix<double>;
%template(Matrix_Point2Dd) PLib::Matrix<PLib::Point2Dd>;
%template(Matrix_Point3Dd) PLib::Matrix<PLib::Point3Dd>;
%template(Matrix_HPoint3Dd) PLib::Matrix<PLib::HPoint3Dd>;
%template(Matrix_HPoint2Dd) PLib::Matrix<PLib::HPoint2Dd>;
