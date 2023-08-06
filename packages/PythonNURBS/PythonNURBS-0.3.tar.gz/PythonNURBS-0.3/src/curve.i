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

%module NurbsCurve
%{
#include <nurbs++/nurbsS.h>
#include <nurbs++/curve.h>
#include <nurbs++/nurbs.h>
%}

%import General.i
%import vector.i
%import hpoint_nd.i
%import point_nd.i
%import color.i
%import matrix.i
%import matrixRT.i

%include "cpointer.i"

%pointer_class(double, doublep);

%include nurbs++/curve.h

%template(ParaCurve3d) PLib::ParaCurve<double, 3>;
%template(ParaCurve2d) PLib::ParaCurve<double, 2>;

%ignore C;
%ignore Cp;
%rename(generateCompatibleCurves) generateCompatibleCurves;

%include nurbs++/nurbs.h

%template(NurbsCurve2Dd) PLib::NurbsCurve<double, 2>;
%template(NurbsCurved) PLib::NurbsCurve<double, 3>;
%template(NurbsCurveArray2Dd) PLib::NurbsCurveArray<double, 2>;
%template(NurbsCurveArrayd) PLib::NurbsCurveArray<double, 3>;

%pointer_class(PLib::NurbsCurved,NurbsCurvedp);
