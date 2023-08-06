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

%module NurbsBasicArray
%{
#include <nurbs++/barray.h>
%} 

%import General.i
%import point_nd.i
%import hpoint_nd.i

%ignore *::operator[];

%rename(equals) 	operator==;
%rename(notequals) 	operator!=;
%rename(in_op) 		operator<<;
%rename(out_op) 	operator>>;

%extend PLib::BasicArray {
	inline T 	__getitem__(int i) { return $self->operator[](i); }
	inline void	__setitem__(int i, T value) { $self->operator[](i) = value; }
}

namespace PLib {
  template <class T> class BasicArray ;

  template <class T> int operator!=(const BasicArray<T>&,const BasicArray<T>&);
  template <class T> int operator==(const BasicArray<T>&,const BasicArray<T>&);
  template <class T> istream& operator>>(istream& is, BasicArray<T>& arry);
  template <class T> ostream& operator<<(ostream& os, const BasicArray<T>& arry);

#include "galloc.h"

template<class T> class BasicArray
{
public:
  int n() const;
  BasicArray();
  BasicArray(const int ni);
  BasicArray(const BasicArray<T>& f2);
  BasicArray(T* ap, const int size);  
  BasicArray(BasicList<T>& list) ;
  virtual ~BasicArray();
  
  BasicArray<T>& operator=(const BasicArray<T>& f2);
  
  int size() const;
  void resize(const int nsize);
  void resize(const BasicArray<T>& A);
  
  void trim(const int nsize);
  void clear();
  void untrim();
  
  T& push_back(const T i, int end_buffer=10, double end_mult=-1);

  
  virtual void reset(const T val = 0.0);
  T operator=(const T val);
  
#ifdef DEBUG_PLIB
  T& operator[](const int i);
  T  operator[](const int i) const;
#else
  T& operator[](const int i);
  T  operator[](const int i);
#endif
  T* memory() const;
  void width(const int w);

#ifdef HAVE_ISO_FRIEND_DECL
  friend int operator!= <>(const BasicArray<T>&,const BasicArray<T>&);
  friend int operator== <>(const BasicArray<T>&,const BasicArray<T>&);
  friend istream& operator>> <>(istream& is, BasicArray<T>& arry);
  friend ostream& operator<< <>(ostream& os, const BasicArray<T>& arry);
#else
  friend int operator!= (const BasicArray<T>&,const BasicArray<T>&);
  friend int operator== (const BasicArray<T>&,const BasicArray<T>&);
  friend istream& operator>> (istream& is, BasicArray<T>& arry);
  friend ostream& operator<< (ostream& os, const BasicArray<T>& arry);
#endif

  ostream& print(ostream& os) const;

  //FRIEND_ARRAY_ALLOCATOR 

  typedef T* iterator ;
  typedef const T* const_iterator ;

  iterator begin();
  const_iterator begin() const;

  iterator end();
  const_iterator end() const;

protected:
  int rsize;
  int wdth;
  int destruct;
  int sze;
  T *x;
};

}

%template(BasicArray_HPoint2Dd) PLib::BasicArray<PLib::HPoint2Dd>;
%template(BasicArray_HPoint3Dd) PLib::BasicArray<PLib::HPoint3Dd>;
%template(BasicArray_Point2Dd)	PLib::BasicArray<PLib::Point2Dd>;
%template(BasicArray_Point3Dd)	PLib::BasicArray<PLib::Point3Dd>;
%template(BasicArray_INT)	PLib::BasicArray<int>;
%template(BasicArray_DOUBLE)	PLib::BasicArray<double>;
