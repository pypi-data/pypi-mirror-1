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

%module NurbsHPoint
%{
#include <nurbs++/hpoint_nd.h>
%}

%import General.i
%import point_nd.i

//Ursprüngliche Funktionen wegrationalisieren, da sie so in Python nicht funktionieren
%ignore *::x;
%ignore *::y;
%ignore *::z;
%ignore *::w;

//Sie werden als get/set-Funktion wiedergeboren
%extend PLib::HPoint_nD<float,3> {
	inline T getx() { return $self->x(); }
	inline T gety() { return $self->y(); }
	inline T getz() { return $self->z(); }
	inline T getw() { return $self->w(); }
	inline void setx(T wert) { $self->x() = wert; }
	inline void sety(T wert) { $self->y() = wert; }
	inline void setz(T wert) { $self->z() = wert; }
	inline void setw(T wert) { $self->w() = wert; }
}

%extend PLib::HPoint_nD<double,3> {
	inline T getx() { return $self->x(); }
	inline T gety() { return $self->y(); }
	inline T getz() { return $self->z(); }
	inline T getw() { return $self->w(); }
	inline void setx(T wert) { $self->x() = wert; }
	inline void sety(T wert) { $self->y() = wert; }
	inline void setz(T wert) { $self->z() = wert; }
	inline void setw(T wert) { $self->w() = wert; }
}

%extend PLib::HPoint_nD<float,2> {
	inline T getx() { return $self->x(); }
	inline T gety() { return $self->y(); }
	inline T getz() { return $self->z(); }
	inline T getw() { return $self->w(); }
	inline void setx(T wert) { $self->x() = wert; }
	inline void sety(T wert) { $self->y() = wert; }
	inline void setz(T wert) { $self->z() = wert; }
	inline void setw(T wert) { $self->w() = wert; }
}

%extend PLib::HPoint_nD<double,2> {
	inline T getx() { return $self->x(); }
	inline T gety() { return $self->y(); }
	inline T getz() { return $self->z(); }
	inline T getw() { return $self->w(); }
	inline void setx(T wert) { $self->x() = wert; }
	inline void sety(T wert) { $self->y() = wert; }
	inline void setz(T wert) { $self->z() = wert; }
	inline void setw(T wert) { $self->w() = wert; }
}

%include nurbs++/hpoint_nd.h

%template(HPoint3Df) PLib::HPoint_nD<float,3>;
%template(HPoint2Df) PLib::HPoint_nD<float,2>;
%template(HPoint3Dd) PLib::HPoint_nD<double,3>;
%template(HPoint2Dd) PLib::HPoint_nD<double,2>;
