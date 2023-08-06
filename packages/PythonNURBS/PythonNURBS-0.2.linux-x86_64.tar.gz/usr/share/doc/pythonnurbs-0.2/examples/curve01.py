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

import math
from pythonnurbs import NurbsCurve, NurbsPoint, NurbsVector

# Printing Options
cp   = 1
magf = 1
dash = 2

radius = 100.0

curve=NurbsCurve.NurbsCurved()
point=NurbsPoint.Point3Dd(0.0,0.0,0.0)
curve.makeCircle(point, radius, 0.0, 2.0*math.pi)
curve.writePS("curve01.ps",cp,magf,dash)
curve.writePS("curve.ps")

curve.writeVRML97("curve97.wrl")
#curve.writeVRML97("curve97.wrl",0.5)

print curve.length()
print curve.length(0.000001,100)
print curve.lengthIn(0.0,1.0,0.000001,100)
print 2*math.pi*radius

u = 0.0

point = curve.pointAt(u)
pointX = point.getx()
pointY = point.gety()
pointZ = point.getz()
pointNorm =  point.norm()
pointNorm2 = point.norm2()

print pointX, pointY, pointZ, pointNorm, pointNorm2

derivationVector = NurbsVector.Vector_Point3Dd()
curve.deriveAt(u,1,derivationVector)
pointNew = curve.derive3D(u,1)

pointH = curve.derive(u,1)
pointHH = curve.firstD(u)

derivationVector.size()
firstDerivation = derivationVector[1]

print firstDerivation.getx(), firstDerivation.gety(), firstDerivation.getz()
print pointNew.getx(), pointNew.gety(), pointNew.getz()

normalA = NurbsPoint.Point3Dd(0,0,0)
normalA.setz(1)
normal = curve.normal(u,normalA)
print normal.getx(), normal.gety(), normal.getz()

xValue = 70.0
uValue = NurbsCurve.doublep()
curve.minDistX(xValue,uValue)
print uValue.value()


curve2=NurbsCurve.NurbsCurved()
curve2.makeCircle(point, radius, 0.0, math.pi)
curve2.writePS("curve2A.ps",cp,magf,dash)

curve2.setTangent(0.0,NurbsPoint.Point3Dd(-0.1,0.1,0))
curve2.writePS("curve2B.ps",cp,magf,dash)

curve2.setTangentAtEnd(NurbsPoint.Point3Dd(0.1,0.1,0),NurbsPoint.Point3Dd(0.1,-0.1,0))
curve2.writePS("curve2C.ps",cp,magf,dash)
