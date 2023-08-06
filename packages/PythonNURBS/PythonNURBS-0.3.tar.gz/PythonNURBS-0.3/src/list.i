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

%module NurbsBasicList
%{
#include <nurbs++/list.h>
%}

%import General.i

%ignore *::operator[];

/*%extend BasicList {
	inline BasicNode<T> 	__getitem__(int i) { return *$self->operator[](i); }
	inline void 		__setitem__(int i, BasicNode<T> Node) { $self->operator[](i) = Node; }
}*/

%extend BasicNode {
	inline T 	getdata() { return *$self->data; }
	inline void	setdata(T value) {
			if(!$self->data)
				$self->data = new T(value);
			else
				*$self->data = value;
		}
}

%extend BasicList {
	inline BasicNode<T>*	__getitem__(int i) { return $self->operator[](i); }
	//inline void		__setitem__(int i, BasicNode<T>* val) { $self->operator[](i) = val; }
}

%include nurbs++/list.h

//%template(BasicNode_DOUBLE) 	BasicNode<double>;
//%template(BasicList_DOUBLE) 	BasicList<double>;
%template(BasicNode_Point2Dd)	BasicNode<PLib::Point2Dd>;
%template(BasicList_Point2Dd) 	BasicList<PLib::Point2Dd>;
%template(BasicNode_Point3Dd)	BasicNode<PLib::Point3Dd>;
%template(BasicList_Point3Dd) 	BasicList<PLib::Point3Dd>;