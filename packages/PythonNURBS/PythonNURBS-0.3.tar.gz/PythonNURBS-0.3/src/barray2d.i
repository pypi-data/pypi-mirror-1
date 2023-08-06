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
%module NurbsArray2D
%{
#include <nurbs++/barray2d.h>
%}

%import General.i
%import point_nd.i
%import hpoint_nd.i

%ignore *::operator[];
%ignore *::operator();
%ignore *::elem;

%rename(in_op) operator<<;
%rename(out_op) operator>>;

%extend PLib::Basic2DArray {
	inline T 	__getitem__(int i) { return *$self->operator[](i); }
	inline void	__setitem__(int i, T value) { *$self->operator[](i) = value; }
	inline T	getelem(const int i, const int j) { return $self->elem(i, j); }
	inline void	setelem(const int i, const int j, T value) { $self->elem(i, j) = value; }
}

namespace PLib {
  template <class T> class Basic2DArray ;

  template <class T> istream& operator>>(istream& is, Basic2DArray<T>& ary);
  template <class T> ostream& operator<<(ostream& os, const Basic2DArray<T>& ary);


#include "galloc2d.h"

template<class T> class Basic2DArray
{
public:
  int rows() const;
  int cols() const;
  Basic2DArray() ;
  Basic2DArray(const int r, const int c) ;
  Basic2DArray(const Basic2DArray<T>& f2);
  Basic2DArray(T* p, const int r, const int c) ;
  
  virtual ~Basic2DArray();
  
  Basic2DArray<T>& operator=(const Basic2DArray<T>& f2);
  
  void resize(const int nr, const int nc); 
  void resize(const Basic2DArray<T>& A);
  void resizeKeep(const int nr, const int nc);

  void reset(const T val = 0.0);
  
  T operator=(const T val);

  T* operator[](const int i);
  
  T& operator()(const int i,const int j);
  T  operator()(const int i,const int j) const;

  void io_elem_width(int w);
  void io_by_rows(); 
  void io_by_columns();



  ostream& print(ostream& os) const ; 

#ifdef HAVE_ISO_FRIEND_DECL
  friend istream& operator>> <>(istream& is, Basic2DArray<T>& ary);
  friend ostream& operator<< <>(ostream& os, const Basic2DArray<T>& ary);
#else
  friend istream& operator>> (istream& is, Basic2DArray<T>& ary);
  friend ostream& operator<< (ostream& os, const Basic2DArray<T>& ary);
#endif

#ifdef DEBUG_PLIB
  T& elem(const int i,const int j);
  T  elem(const int i,const int j) const;
#else
#ifdef COLUMN_ORDER
  T& elem(const int i,const int j);
  T  elem(const int i,const int j) const;
#else
  T& elem(const int i,const int j) ;
  T  elem(const int i,const int j) const;
#endif
#endif
  
  //FRIEND_2DARRAY_ALLOCATOR


  
protected:
  int by_columns;
  int width;
  int rz; 
  int cz; 
  T *m;  
  T **vm ;  
  int created ;

  void init(const int r = 1, const int c = 1);

};

}

%template(Array2D_INT) PLib::Basic2DArray<int>;
%template(Array2D_DOUBLE) PLib::Basic2DArray<double>;
%template(Array2D_Point2Dd) PLib::Basic2DArray<PLib::Point2Dd>;
%template(Array2D_Point3Dd) PLib::Basic2DArray<PLib::Point3Dd>;
%template(Array2D_HPoint2Dd) PLib::Basic2DArray<PLib::HPoint2Dd>;
%template(Array2D_HPoint3Dd) PLib::Basic2DArray<PLib::HPoint3Dd>;
