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

radius = 100.0

curve=NurbsCurve.NurbsCurved()
point=NurbsPoint.Point3Dd(0.0,0.0,0.0)
curve.makeCircle(point, radius, 0.0, 2.0*math.pi)

maxPoints = 100

pointsB = NurbsVector.Vector_Point3Dd(maxPoints)
vector = NurbsVector.Vector_Point3Dd(1)
pointsBNew = NurbsVector.Vector_Point3Dd(maxPoints)

for n in range(maxPoints):
	vector.reset(curve.pointAt(1.0/(maxPoints-1)*n))
	pointsB.as_func(n,vector)
	pointsBNew[n] = curve.pointAt(1.0/(maxPoints-1)*n)

curveA = NurbsCurve.NurbsCurved()
curveB = NurbsCurve.NurbsCurved()
curveC = NurbsCurve.NurbsCurved()
curveD = NurbsCurve.NurbsCurved()
curveE = NurbsCurve.NurbsCurved()

# Printing Options
cp   = 1
magf = 1
dash = 2

curveA.globalInterp(pointsB,3)
curveB.leastSquares(pointsB,3,12)
curveC.leastSquaresClosed(pointsB,3,12)
curveD.globalApproxErrBnd(pointsB,3,10)
curveE.globalApproxErrBnd3(pointsBNew,3,10)

curveD.writePS("curveD_10.ps",cp,magf,dash)
curveD.globalApproxErrBnd3(pointsB,3,1)
curveD.writePS("curveD_1.ps",cp,magf,dash)
curveD.globalApproxErrBnd3(pointsB,3,0.1)
curveD.writePS("curveD_01.ps",cp,magf,dash)

curveA.writePS("curveA.ps",cp,magf,dash)
curveB.writePS("curveB.ps",cp,magf,dash)
#curveC.writePS("curveC.ps",cp,magf,dash)
curveD.writePS("curveD.ps",cp,magf,dash)
curveE.writePS("curveE.ps",cp,magf,dash)

curveA.writeVRML97("curveA.wrl")
