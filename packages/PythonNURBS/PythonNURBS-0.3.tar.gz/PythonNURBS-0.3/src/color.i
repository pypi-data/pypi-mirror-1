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

%module NurbsColor
%{
#include <nurbs++/color.h>
%}

%import General.i

%rename(mul) operator*(const double, const Color&);
%rename(mul) operator*(const Color&, const Color&);

%rename(add) operator+(const Color&, const Color&);

%rename(in_op) operator<<(ostream&, const Color&);
%rename(out_op) operator>>(istream&, Color&);

namespace PLib {
  class Color {
  public:
    unsigned char r,g,b ;
    Color(const unsigned char R=0, const unsigned char G=0, const unsigned char B=0) : r(R),g(G),b(B) {} 
    Color& operator+=(const Color& a);
    Color& operator-=(const Color& a);
    Color& operator*=(double a);
    Color& operator/=(double a);
    Color& operator=(const Color& a);

    void fromXYZ(double x, double y, double z) ;
    void toXYZ(double& x, double& y, double& z) ;

    void fromYIQ(double q, double i, double y);
    void toYIQ(double& q, double& i, double& y);

    void fromHSV(double h, double s, double v);
    void toHSV(double& h, double& s, double& v);


    friend Color operator*(const double d, const Color& a) ; // multiplies a color by a double 
    friend Color operator*(const Color& a, const Color& b) ; // multiplies a color by another color
    friend Color operator+(const Color& a, const Color& b) ; // Addition of two colors
    
    
    friend ostream& operator<<(ostream& os, const Color& point);
    friend istream& operator>>(istream& os, Color& point);
  };
  
  int operator==(const Color& a, const Color& b);
  int operator!=(const Color& a, const Color& b);
  int operator<(const Color& a, const Color& b);
  int operator>(const Color& a, const Color& b);
  int operator<=(const Color& a, const Color& b);
  int operator>=(const Color& a, const Color& b);
  
  /*const Color whiteColor(255,255,255);
  const Color redColor(255,0,0) ;
  const Color blueColor(0,0,255) ;
  const Color greenColor(0,255,0) ;
  const Color yellowColor(255,255,0) ;
  const Color cyanColor(0,255,255) ;
  const Color magentaColor(255,0,255);
  const Color gray80Color(204,204,204) ;
  const Color gray50Color(127,127,127) ;
  const Color blackColor(0,0,0) ;*/
  /*
  extern Color whiteColor ;
  extern Color redColor ;
  extern Color blueColor ;
  extern Color greenColor ;
  extern Color yellowColor ;
  extern Color cyanColor ;
  extern Color magentaColor ;
  extern Color gray80Color ;
  extern Color gray50Color ;
  extern Color blackColor ;
  */

  Color operator*(const double d, const Color& a);
  Color operator*(const Color& a, const Color& b);
  Color operator+(const Color& a, const Color& b);


  class ColorF {
  public:
    float r,g,b ;
    ColorF(float R=0.0, float G=0.0, float B=0.0) : r(R),g(G),b(B) {} 
    ColorF& operator=(const ColorF& a);
  };
  

  ostream& operator<<(ostream& os,const Color& c);
  istream& operator>>(istream& os, Color& c);
}