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

%module NurbsSurface
%{
#include <nurbs++/nurbs.h>
#include <nurbs++/surface.h>
#include <nurbs++/nurbsS.h>
%}

%import General.i
%import point_nd.i
%import hpoint_nd.i
%import matrix.i
%import color.i
%import curve.i
%import coordinate.i

%pointer_class(double, doublep);

%include nurbs++/surface.h

%template(ParaSurface3d) PLib::ParaSurface<double, 3>;

%rename(gordonSurface) gordonSurface;
%rename(globalSurfInterpXY) globalSurfInterpXY;
%rename(globalSurfApprox) globalSurfApprox;

//Zugriffe bzw Referenzen
%ignore modU;
%ignore modV;

%extend PLib::NurbsSurface {
	inline T 	getmodU(int i) { return $self->modU(i); }
	inline void	setmodU(int i, T val) { $self->modU(i) = val; }
	inline T 	getmodV(int i) { return $self->modV(i); }
	inline void	setmodV(int i, T val) { $self->modV(i) = val; }
}

%include nurbs++/nurbsS.h

%template(NurbsSurfaced) PLib::NurbsSurface<double, 3>;
