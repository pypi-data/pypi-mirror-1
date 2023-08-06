#!/usr/bin/env python
# -*- coding: utf-8 -*-

#***************************************************************************
#*   Copyright (C) 2008-2009 by Oliver Borm                                *
#*   oli.borm@web.de                                                       *
#*                                                                         *
#*   This program is free software; you can redistribute it and/or modify  *
#*   it under the terms of the GNU General Public License as published by  *
#*   the Free Software Foundation; either version 3 of the License, or     *
#*   (at your option) any later version.                                   *
#*                                                                         *
#*   This program is distributed in the hope that it will be useful,       *
#*   but WITHOUT ANY WARRANTY; without even the implied warranty of        *
#*   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         *
#*   GNU General Public License for more details.                          *
#*                                                                         *
#*   You should have received a copy of the GNU General Public License     *
#*   along with this program; if not, write to the                         *
#*   Free Software Foundation, Inc.,                                       *
#*   59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.             *
#***************************************************************************

# Author: Oliver Borm
# Date: March 2009

from pythonnurbs import NurbsCurve
from pythonnurbs import NurbsPoint
from pythonnurbs import NurbsHPoint
from pythonnurbs import NurbsVector
from pythonnurbs import NurbsMatrixRT
from pythonnurbs import NurbsMatrix
from pythonnurbs import NurbsSurface
from pythonnurbs import NurbsColor

print "Members from NurbsCurveD: "
print dir(NurbsCurve)
print 
print "Members from NurbsPointD: "
print dir(NurbsPoint)
print 
print "Members from NurbsHPointD: "
print dir(NurbsHPoint)
print 
print "Members from NurbsVectorD: "
print dir(NurbsVector)
print 
print "Members from NurbsMatrixRTD: "
print dir(NurbsMatrixRT)
print 
print "Members from NurbsMatrixD: "
print dir(NurbsMatrix)
print 
print "Members from NurbsSurfaceD: "
print dir(NurbsSurface)
print 
print "Members from NurbsColor: "
print dir(NurbsColor)
