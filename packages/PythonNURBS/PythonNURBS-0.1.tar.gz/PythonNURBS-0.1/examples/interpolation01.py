#!/usr/bin/env python
# -*- coding: utf-8 -*-

#***************************************************************************
#*   Copyright (C) 2008-2008 by Oliver Borm                                *
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
# Date: February 2008

from numpy import zeros
import NurbsCurveD
import NurbsPointD
import NurbsVectorD

maxPoints = 10
coordinates = zeros([3,maxPoints], 'd')

## x-coordinates
coordinates[0,0] = 20.0
coordinates[0,1] = 20.0
coordinates[0,2] = 20.0
coordinates[0,3] = 20.0
coordinates[0,4] = 80.0
coordinates[0,5] = 120.0
coordinates[0,6] = 160.0
coordinates[0,7] = 160.0
coordinates[0,8] = 120.0
coordinates[0,9] = 80.0

## y-coordinates
coordinates[1,0] = 20.0
coordinates[1,1] = 80.0
coordinates[1,2] = 120.0
coordinates[1,3] = 160.0
coordinates[1,4] = 200.0
coordinates[1,5] = 200.0
coordinates[1,6] = 160.0
coordinates[1,7] = 120.0
coordinates[1,8] = 80.0
coordinates[1,9] = 80.0

## z-coordinates
coordinates[2,0] = 0.0
coordinates[2,1] = 0.0
coordinates[2,2] = 0.0
coordinates[2,3] = 0.0
coordinates[2,4] = 0.0
coordinates[2,5] = 0.0
coordinates[2,6] = 0.0
coordinates[2,7] = 0.0
coordinates[2,8] = 0.0
coordinates[2,9] = 0.0

pointsB = NurbsVectorD.Vector_Point3Dd(maxPoints)
vector = NurbsVectorD.Vector_Point3Dd(1)

for n in range(maxPoints):
	vector.reset(NurbsPointD.Point3Dd(coordinates[0,n],coordinates[1,n],coordinates[2,n]))
	pointsB.as(n,vector)


curveA = NurbsCurveD.NurbsCurve3Dd()
curveB = NurbsCurveD.NurbsCurve3Dd()
curveC = NurbsCurveD.NurbsCurve3Dd()
curveD = NurbsCurveD.NurbsCurve3Dd()

curveA.globalInterp(pointsB,3)
curveB.leastSquares(pointsB,3,pointsB.n()-2)
curveC.leastSquares(pointsB,3,pointsB.n()-4)
## curveD.globalApproxErrBnd(pointsB,3,10) doesn't work yet!
curveD.globalApproxErrBnd3(pointsB,3,10)

# Printing Options
cp   = 1
magf = 1
dash = 2

curveA.writePS("curveA.ps",cp,magf,dash)
curveB.writePS("curveB.ps",cp,magf,dash)
curveC.writePS("curveC.ps",cp,magf,dash)
curveD.writePS("curveD.ps",cp,magf,dash)

#curveA.writeVRML97("curveA.wrl")
