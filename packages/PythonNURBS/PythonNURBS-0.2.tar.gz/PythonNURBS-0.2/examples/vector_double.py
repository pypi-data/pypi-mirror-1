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

from pythonnurbs import NurbsCurve, NurbsPoint, NurbsVector

maxPoints = 10
deg = 3
lengthKnoten = maxPoints+deg+1
plotting = False

weights = NurbsVector.Vector_DOUBLE(maxPoints)
knots = NurbsVector.Vector_DOUBLE(lengthKnoten)

for n in range(maxPoints):
	weights[n] = 1.0

for n in range(lengthKnoten):
	if n < deg-1:
		dummy = 0.0
	elif n > (lengthKnoten-deg):
		dummy = 1.0
	else:
		dummy = (n-(deg-1))*1.0/(maxPoints-1)
	
	print dummy
	knots[n] = dummy

coordinates = range(3)

for i in range(3):
	coordinates[i] = range(maxPoints)

## x-coordinates
coordinates[0][0] = 20.0
coordinates[0][1] = 20.0
coordinates[0][2] = 20.0
coordinates[0][3] = 20.0
coordinates[0][4] = 80.0
coordinates[0][5] = 120.0
coordinates[0][6] = 160.0
coordinates[0][7] = 160.0
coordinates[0][8] = 120.0
coordinates[0][9] = 80.0

## y-coordinates
coordinates[1][0] = 20.0
coordinates[1][1] = 80.0
coordinates[1][2] = 120.0
coordinates[1][3] = 160.0
coordinates[1][4] = 200.0
coordinates[1][5] = 200.0
coordinates[1][6] = 160.0
coordinates[1][7] = 120.0
coordinates[1][8] = 80.0
coordinates[1][9] = 80.0

pointsB = NurbsVector.Vector_Point2Dd(maxPoints)
vector = NurbsVector.Vector_Point2Dd(1)

for n in range(maxPoints):
	vector.reset(NurbsPoint.Point2Dd(coordinates[0][n],coordinates[1][n]))
	pointsB.as_func(n,vector)
	

curveA = NurbsCurve.NurbsCurve2Dd()
curveB = NurbsCurve.NurbsCurve2Dd(pointsB,weights,knots,deg)
curveC = NurbsCurve.NurbsCurve2Dd()

## working
curveA.globalInterp(pointsB,deg)
curveC.leastSquares(pointsB,deg,8)

## not working
#curveA.globalInterp(pointsB,knots,deg)
#curveC.leastSquaresClosed(pointsB,deg,8)

if plotting == True:
	import pylab as p
	pnts = 100
	coordinates2 = range(2)
	coordinates3 = range(2)
	coordinates4 = range(2)
	
	for i in range(2):
		coordinates2[i] = range(pnts)
		coordinates3[i] = range(pnts)
		coordinates4[i] = range(pnts)
	
	for i in range(100):
		point = curveA.pointAt(i*1.0/(99.0))
		coordinates2[0][i] = point.getx()
		coordinates2[1][i] = point.gety()
		
		point = curveB.pointAt(i*1.0/(99.0))
		coordinates3[0][i] = point.getx()
		coordinates3[1][i] = point.gety()
		
		point = curveC.pointAt(i*1.0/(99.0))
		coordinates4[0][i] = point.getx()
		coordinates4[1][i] = point.gety()
		print point.getx(),point.gety()
	
	fig=p.figure()
	#p.plot(coordinates2[0],coordinates2[1])
	p.plot(coordinates3[:][0],coordinates3[:][1])
	#p.plot(coordinates4[0],coordinates4[1])
	p.show()

# Printing Options
cp   = 1
magf = 1
dash = 2

curveA.writePS("curveA.ps")
#curveB.writePS("curveB.ps")	# does not work yet, also not in C++
curveC.writePS("curveC.ps")
