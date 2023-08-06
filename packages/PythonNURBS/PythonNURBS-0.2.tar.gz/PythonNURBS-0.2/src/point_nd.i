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

%module NurbsPoint
%{
#include <nurbs++/point_nd.h>
%} 

%import General.i

%ignore PLib::maximum;
%ignore PLib::minimum;
%ignore *::x;
%ignore *::y;
%ignore *::z;

%extend PLib::Point_nD<double,2> {
	inline T getx() { return $self->x(); }
	inline T gety() { return $self->y(); }
	inline void setx(T wert) { $self->x() = wert; }
	inline void sety(T wert) { $self->y() = wert; }
}

%extend PLib::Point_nD<float,2> {
	inline T getx() { return $self->x(); }
	inline T gety() { return $self->y(); }
	inline void setx(T wert) { $self->x() = wert; }
	inline void sety(T wert) { $self->y() = wert; }
}

%extend PLib::Point_nD<double,3> {
	inline T getx() { return $self->x(); }
	inline T gety() { return $self->y(); }
	inline T getz() { return $self->z(); }
	inline void setx(T wert) { $self->x() = wert; }
	inline void sety(T wert) { $self->y() = wert; }
	inline void setz(T wert) { $self->z() = wert; }
}

%extend PLib::Point_nD<float,3> {
	inline T getx() { return $self->x(); }
	inline T gety() { return $self->y(); }
	inline T getz() { return $self->z(); }
	inline void setx(T wert) { $self->x() = wert; }
	inline void sety(T wert) { $self->y() = wert; }
	inline void setz(T wert) { $self->z() = wert; }
}

%include nurbs++/point_nd.h

#Klassen wrappen
%template(Point2Dd) PLib::Point_nD<double,2>;
%template(Point3Dd) PLib::Point_nD<double,3>;
%template(Point2Df) PLib::Point_nD<float,2>;
%template(Point3Df) PLib::Point_nD<float,3>;

#Zusatzfunktionen wrappen
%template(norm2) PLib::norm2<double, 2>;
%template(norm2) PLib::norm2<double, 3>;
%template(norm2) PLib::norm2<float, 2>;
%template(norm2) PLib::norm2<float, 3>;

%template(norm) PLib::norm<double, 2>;
%template(norm) PLib::norm<double, 3>;
%template(norm) PLib::norm<float, 2>;
%template(norm) PLib::norm<float, 3>;

%template(angle) PLib::angle<double, 2>;
%template(angle) PLib::angle<double, 3>;
%template(angle) PLib::angle<float, 2>;
%template(angle) PLib::angle<float, 3>;

%template(crossProduct) PLib::crossProduct<double>;
%template(crossProduct) PLib::crossProduct<float>;

%template(dot) PLib::dot<double>;
%template(dot) PLib::dot<float>;

//%template(maximumByRef) PLib::maximumByRef<float>;
//%template(maximumByRef) PLib::maximumByRef<double>;
//%template(minimumByRef) PLib::minimumByRef<double>;
//%template(minimumByRef) PLib::minimumByRef<float>;
