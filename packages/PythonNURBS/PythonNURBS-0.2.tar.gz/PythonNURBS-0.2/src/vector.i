
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

%module NurbsVector
%{
#include <nurbs++/vector.h>
%}

%import General.i
%import barray.i
%import point_nd.i
%import hpoint_nd.i

%rename(mul) 		operator*;
%rename(add) 		operator+;
%rename(sub) 		operator-;
%rename(equals)		operator==;
%rename(notequals)	operator!=;
%rename(as_func)	PLib::Vector::as;

namespace PLib {

  template <class T> class Vector ;

  template <class T> Vector<T> operator+(const Vector<T>&, const Vector<T>&);
  template <class T> Vector<T> operator-(const Vector<T>&, const Vector<T>&);

  template <class T> T operator*(const Vector<T>&,const Vector<T>&); 
  template <class T> Vector<T> operator*(const Vector<T>& v, const double d);
  template <class T> Vector<T> operator*(const Vector<T>& v, const Complex d);
		    
  template <class T> Vector<T> operator*(const double d,const Vector<T>& v) ;
  template <class T> Vector<T> operator*(const Complex d,const Vector<T>& v) ;

  template<> Vector<Complex>  operator*(const Vector<Complex>& v, const double d);
  template <> Vector<Complex>  operator*(const Vector<Complex>& v, const Complex d);

  template <class T> int operator==(const Vector<T>&,const Vector<T>&);
  template <class T> int operator!=(const Vector<T>& a,const Vector<T>& b);

  template<class T> class Vector : public BasicArray<T>
  {
  public:
    int rows() const;
    Vector() : BasicArray<T>(1) {} //!< Basic constructor
    Vector(const int r) : BasicArray<T>(r) {}
    Vector(const Vector<T>& v) : BasicArray<T>(v) {}
    Vector(const BasicArray<T>& v) : BasicArray<T>(v)  {}
    Vector(T* ap, const int size) : BasicArray<T>(ap,size) {}
    Vector(BasicList<T>& list) : BasicArray<T>(list) {}
    
    virtual ~Vector() {}
    
    Vector<T>& operator=(const Vector<T>& v);
    Vector<T>& operator=(const BasicArray<T>& b);
    
    Vector<T>& operator+=(const Vector<T>& a);
    Vector<T>& operator-=(const Vector<T>& a);
    
    T operator=(const T d);
    void as(int i, const Vector<T>& b);
    Vector<T> get(int i, int l);
    
    int minIndex() const ;
    T minimum() const;
    
    void qSortStd() ;
    void qSort(int M=7) ; 
    void sortIndex(Vector<int>& index, int M=7) const;
    
    
#ifdef HAVE_ISO_FRIEND_DECL
    friend Vector<T> operator+ <>(const Vector<T> &a, const Vector<T> &b);
    friend Vector<T> operator- <>(const Vector<T> &a, const Vector<T> &b);
    friend T operator* <>(const Vector<T> &a,const Vector<T> &b); 
    
    friend Vector<T> operator* <>(const Vector<T>& v, const double d);
    friend Vector<T> operator* <>(const Vector<T>& v, const Complex d);
    
    friend Vector<T> operator* <>(const double d,const Vector<T>& v) ;
    friend Vector<T> operator* <>(const Complex d,const Vector<T>& v) ;
    
    friend int operator== <>(const Vector<T> &a,const Vector<T> &b);
    friend int operator!= <>(const Vector<T>& a,const Vector<T>& b);
    
#else
    friend Vector<T> operator+(const Vector<T> &a, const Vector<T> &b);
    friend Vector<T> operator-(const Vector<T> &a, const Vector<T> &b);
    friend T operator* (const Vector<T> &a,const Vector<T> &b); 
    
    friend Vector<T> operator*(const Vector<T>& v, const double d);
    friend Vector<T> operator*(const Vector<T>& v, const Complex d);
    			      
    friend Vector<T> operator*(const double d,const Vector<T>& v) ;
    friend Vector<T> operator*(const Complex d,const Vector<T>& v) ;
    
    friend int operator==(const Vector<T> &a,const Vector<T> &b);
    friend int operator!=(const Vector<T>& a,const Vector<T>& b);
    
#endif
    
  };
}
%template(Vector_INT)		PLib::Vector<int>;
%template(Vector_DOUBLE) 	PLib::Vector<double>;

%template(Vector_Point2Dd)	PLib::Vector<PLib::Point2Dd>;
%template(Vector_Point3Dd)	PLib::Vector<PLib::Point3Dd>;

%template(Vector_HPoint2Dd)	PLib::Vector<PLib::HPoint2Dd>;
%template(Vector_HPoint3Dd)	PLib::Vector<PLib::HPoint3Dd>;

