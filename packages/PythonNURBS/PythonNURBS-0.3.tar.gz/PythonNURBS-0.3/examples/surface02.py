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
# Date: October 2009

import scipy.optimize
import numpy
from pythonnurbs import NurbsPoint, NurbsMatrix, NurbsSurface, NurbsCurve, NurbsColor

maxPoints = 11
degree = 3

coordinates = range(3)
for i in range(3):
	coordinates[i] = range(maxPoints)
	for j in range(maxPoints):
		coordinates[i][j] = range(maxPoints)

coordinates[0][0][0] = -50.0
coordinates[1][0][0] = -18.75
coordinates[2][0][0] = 60.1040764009
coordinates[0][0][1] = -50.0
coordinates[1][0][1] = -15.0
coordinates[2][0][1] = 65.2897388569
coordinates[0][0][2] = -50.0
coordinates[1][0][2] = -11.25
coordinates[2][0][2] = 69.0543264394
coordinates[0][0][3] = -50.0
coordinates[1][0][3] = -7.5
coordinates[2][0][3] = 71.622273072
coordinates[0][0][4] = -50.0
coordinates[1][0][4] = -3.75
coordinates[2][0][4] = 73.1197647699
coordinates[0][0][5] = -50.0
coordinates[1][0][5] = 0.0
coordinates[2][0][5] = 73.6121593217
coordinates[0][0][6] = -50.0
coordinates[1][0][6] = 3.75
coordinates[2][0][6] = 73.1197647699
coordinates[0][0][7] = -50.0
coordinates[1][0][7] = 7.5
coordinates[2][0][7] = 71.622273072
coordinates[0][0][8] = -50.0
coordinates[1][0][8] = 11.25
coordinates[2][0][8] = 69.0543264394
coordinates[0][0][9] = -50.0
coordinates[1][0][9] = 15.0
coordinates[2][0][9] = 65.2897388569
coordinates[0][0][10] = -50.0
coordinates[1][0][10] = 18.75
coordinates[2][0][10] = 60.1040764009
coordinates[0][1][0] = -40.0
coordinates[1][1][0] = -18.75
coordinates[2][1][0] = 65.2897388569
coordinates[0][1][1] = -40.0
coordinates[1][1][1] = -15.0
coordinates[2][1][1] = 70.0927956355
coordinates[0][1][2] = -40.0
coordinates[1][1][2] = -11.25
coordinates[2][1][2] = 73.6121593217
coordinates[0][1][3] = -40.0
coordinates[1][1][3] = -7.5
coordinates[2][1][3] = 76.026311235
coordinates[0][1][4] = -40.0
coordinates[1][1][4] = -3.75
coordinates[2][1][4] = 77.4386854227
coordinates[0][1][5] = -40.0
coordinates[1][1][5] = 0.0
coordinates[2][1][5] = 77.9037868142
coordinates[0][1][6] = -40.0
coordinates[1][1][6] = 3.75
coordinates[2][1][6] = 77.4386854227
coordinates[0][1][7] = -40.0
coordinates[1][1][7] = 7.5
coordinates[2][1][7] = 76.026311235
coordinates[0][1][8] = -40.0
coordinates[1][1][8] = 11.25
coordinates[2][1][8] = 73.6121593217
coordinates[0][1][9] = -40.0
coordinates[1][1][9] = 15.0
coordinates[2][1][9] = 70.0927956355
coordinates[0][1][10] = -40.0
coordinates[1][1][10] = 18.75
coordinates[2][1][10] = 65.2897388569
coordinates[0][2][0] = -30.0
coordinates[1][2][0] = -18.75
coordinates[2][2][0] = 69.0543264394
coordinates[0][2][1] = -30.0
coordinates[1][2][1] = -15.0
coordinates[2][2][1] = 73.6121593217
coordinates[0][2][2] = -30.0
coordinates[1][2][2] = -11.25
coordinates[2][2][2] = 76.9707736742
coordinates[0][2][3] = -30.0
coordinates[1][2][3] = -7.5
coordinates[2][2][3] = 79.2827219513
coordinates[0][2][4] = -30.0
coordinates[1][2][4] = -3.75
coordinates[2][2][4] = 80.6380803343
coordinates[0][2][5] = -30.0
coordinates[1][2][5] = 0.0
coordinates[2][2][5] = 81.0848321204
coordinates[0][2][6] = -30.0
coordinates[1][2][6] = 3.75
coordinates[2][2][6] = 80.6380803343
coordinates[0][2][7] = -30.0
coordinates[1][2][7] = 7.5
coordinates[2][2][7] = 79.2827219513
coordinates[0][2][8] = -30.0
coordinates[1][2][8] = 11.25
coordinates[2][2][8] = 76.9707736742
coordinates[0][2][9] = -30.0
coordinates[1][2][9] = 15.0
coordinates[2][2][9] = 73.6121593217
coordinates[0][2][10] = -30.0
coordinates[1][2][10] = 18.75
coordinates[2][2][10] = 69.0543264394
coordinates[0][3][0] = -20.0
coordinates[1][3][0] = -18.75
coordinates[2][3][0] = 71.622273072
coordinates[0][3][1] = -20.0
coordinates[1][3][1] = -15.0
coordinates[2][3][1] = 76.026311235
coordinates[0][3][2] = -20.0
coordinates[1][3][2] = -11.25
coordinates[2][3][2] = 79.2827219513
coordinates[0][3][3] = -20.0
coordinates[1][3][3] = -7.5
coordinates[2][3][3] = 81.5291358963
coordinates[0][3][4] = -20.0
coordinates[1][3][4] = -3.75
coordinates[2][3][4] = 82.8477519309
coordinates[0][3][5] = -20.0
coordinates[1][3][5] = 0.0
coordinates[2][3][5] = 83.2826512546
coordinates[0][3][6] = -20.0
coordinates[1][3][6] = 3.75
coordinates[2][3][6] = 82.8477519309
coordinates[0][3][7] = -20.0
coordinates[1][3][7] = 7.5
coordinates[2][3][7] = 81.5291358963
coordinates[0][3][8] = -20.0
coordinates[1][3][8] = 11.25
coordinates[2][3][8] = 79.2827219513
coordinates[0][3][9] = -20.0
coordinates[1][3][9] = 15.0
coordinates[2][3][9] = 76.026311235
coordinates[0][3][10] = -20.0
coordinates[1][3][10] = 18.75
coordinates[2][3][10] = 71.622273072
coordinates[0][4][0] = -10.0
coordinates[1][4][0] = -18.75
coordinates[2][4][0] = 73.1197647699
coordinates[0][4][1] = -10.0
coordinates[1][4][1] = -15.0
coordinates[2][4][1] = 77.4386854227
coordinates[0][4][2] = -10.0
coordinates[1][4][2] = -11.25
coordinates[2][4][2] = 80.6380803343
coordinates[0][4][3] = -10.0
coordinates[1][4][3] = -7.5
coordinates[2][4][3] = 82.8477519309
coordinates[0][4][4] = -10.0
coordinates[1][4][4] = -3.75
coordinates[2][4][4] = 84.1457069612
coordinates[0][4][5] = -10.0
coordinates[1][4][5] = 0.0
coordinates[2][4][5] = 84.5739321541
coordinates[0][4][6] = -10.0
coordinates[1][4][6] = 3.75
coordinates[2][4][6] = 84.1457069612
coordinates[0][4][7] = -10.0
coordinates[1][4][7] = 7.5
coordinates[2][4][7] = 82.8477519309
coordinates[0][4][8] = -10.0
coordinates[1][4][8] = 11.25
coordinates[2][4][8] = 80.6380803343
coordinates[0][4][9] = -10.0
coordinates[1][4][9] = 15.0
coordinates[2][4][9] = 77.4386854227
coordinates[0][4][10] = -10.0
coordinates[1][4][10] = 18.75
coordinates[2][4][10] = 73.1197647699
coordinates[0][5][0] = 0.0
coordinates[1][5][0] = -18.75
coordinates[2][5][0] = 73.6121593217
coordinates[0][5][1] = 0.0
coordinates[1][5][1] = -15.0
coordinates[2][5][1] = 77.9037868142
coordinates[0][5][2] = 0.0
coordinates[1][5][2] = -11.25
coordinates[2][5][2] = 81.0848321204
coordinates[0][5][3] = 0.0
coordinates[1][5][3] = -7.5
coordinates[2][5][3] = 83.2826512546
coordinates[0][5][4] = 0.0
coordinates[1][5][4] = -3.75
coordinates[2][5][4] = 84.5739321541
coordinates[0][5][5] = 0.0
coordinates[1][5][5] = 0.0
coordinates[2][5][5] = 85.0
coordinates[0][5][6] = 0.0
coordinates[1][5][6] = 3.75
coordinates[2][5][6] = 84.5739321541
coordinates[0][5][7] = 0.0
coordinates[1][5][7] = 7.5
coordinates[2][5][7] = 83.2826512546
coordinates[0][5][8] = 0.0
coordinates[1][5][8] = 11.25
coordinates[2][5][8] = 81.0848321204
coordinates[0][5][9] = 0.0
coordinates[1][5][9] = 15.0
coordinates[2][5][9] = 77.9037868142
coordinates[0][5][10] = 0.0
coordinates[1][5][10] = 18.75
coordinates[2][5][10] = 73.6121593217
coordinates[0][6][0] = 10.0
coordinates[1][6][0] = -18.75
coordinates[2][6][0] = 73.1197647699
coordinates[0][6][1] = 10.0
coordinates[1][6][1] = -15.0
coordinates[2][6][1] = 77.4386854227
coordinates[0][6][2] = 10.0
coordinates[1][6][2] = -11.25
coordinates[2][6][2] = 80.6380803343
coordinates[0][6][3] = 10.0
coordinates[1][6][3] = -7.5
coordinates[2][6][3] = 82.8477519309
coordinates[0][6][4] = 10.0
coordinates[1][6][4] = -3.75
coordinates[2][6][4] = 84.1457069612
coordinates[0][6][5] = 10.0
coordinates[1][6][5] = 0.0
coordinates[2][6][5] = 84.5739321541
coordinates[0][6][6] = 10.0
coordinates[1][6][6] = 3.75
coordinates[2][6][6] = 84.1457069612
coordinates[0][6][7] = 10.0
coordinates[1][6][7] = 7.5
coordinates[2][6][7] = 82.8477519309
coordinates[0][6][8] = 10.0
coordinates[1][6][8] = 11.25
coordinates[2][6][8] = 80.6380803343
coordinates[0][6][9] = 10.0
coordinates[1][6][9] = 15.0
coordinates[2][6][9] = 77.4386854227
coordinates[0][6][10] = 10.0
coordinates[1][6][10] = 18.75
coordinates[2][6][10] = 73.1197647699
coordinates[0][7][0] = 20.0
coordinates[1][7][0] = -18.75
coordinates[2][7][0] = 71.622273072
coordinates[0][7][1] = 20.0
coordinates[1][7][1] = -15.0
coordinates[2][7][1] = 76.026311235
coordinates[0][7][2] = 20.0
coordinates[1][7][2] = -11.25
coordinates[2][7][2] = 79.2827219513
coordinates[0][7][3] = 20.0
coordinates[1][7][3] = -7.5
coordinates[2][7][3] = 81.5291358963
coordinates[0][7][4] = 20.0
coordinates[1][7][4] = -3.75
coordinates[2][7][4] = 82.8477519309
coordinates[0][7][5] = 20.0
coordinates[1][7][5] = 0.0
coordinates[2][7][5] = 83.2826512546
coordinates[0][7][6] = 20.0
coordinates[1][7][6] = 3.75
coordinates[2][7][6] = 82.8477519309
coordinates[0][7][7] = 20.0
coordinates[1][7][7] = 7.5
coordinates[2][7][7] = 81.5291358963
coordinates[0][7][8] = 20.0
coordinates[1][7][8] = 11.25
coordinates[2][7][8] = 79.2827219513
coordinates[0][7][9] = 20.0
coordinates[1][7][9] = 15.0
coordinates[2][7][9] = 76.026311235
coordinates[0][7][10] = 20.0
coordinates[1][7][10] = 18.75
coordinates[2][7][10] = 71.622273072
coordinates[0][8][0] = 30.0
coordinates[1][8][0] = -18.75
coordinates[2][8][0] = 69.0543264394
coordinates[0][8][1] = 30.0
coordinates[1][8][1] = -15.0
coordinates[2][8][1] = 73.6121593217
coordinates[0][8][2] = 30.0
coordinates[1][8][2] = -11.25
coordinates[2][8][2] = 76.9707736742
coordinates[0][8][3] = 30.0
coordinates[1][8][3] = -7.5
coordinates[2][8][3] = 79.2827219513
coordinates[0][8][4] = 30.0
coordinates[1][8][4] = -3.75
coordinates[2][8][4] = 80.6380803343
coordinates[0][8][5] = 30.0
coordinates[1][8][5] = 0.0
coordinates[2][8][5] = 81.0848321204
coordinates[0][8][6] = 30.0
coordinates[1][8][6] = 3.75
coordinates[2][8][6] = 80.6380803343
coordinates[0][8][7] = 30.0
coordinates[1][8][7] = 7.5
coordinates[2][8][7] = 79.2827219513
coordinates[0][8][8] = 30.0
coordinates[1][8][8] = 11.25
coordinates[2][8][8] = 76.9707736742
coordinates[0][8][9] = 30.0
coordinates[1][8][9] = 15.0
coordinates[2][8][9] = 73.6121593217
coordinates[0][8][10] = 30.0
coordinates[1][8][10] = 18.75
coordinates[2][8][10] = 69.0543264394
coordinates[0][9][0] = 40.0
coordinates[1][9][0] = -18.75
coordinates[2][9][0] = 65.2897388569
coordinates[0][9][1] = 40.0
coordinates[1][9][1] = -15.0
coordinates[2][9][1] = 70.0927956355
coordinates[0][9][2] = 40.0
coordinates[1][9][2] = -11.25
coordinates[2][9][2] = 73.6121593217
coordinates[0][9][3] = 40.0
coordinates[1][9][3] = -7.5
coordinates[2][9][3] = 76.026311235
coordinates[0][9][4] = 40.0
coordinates[1][9][4] = -3.75
coordinates[2][9][4] = 77.4386854227
coordinates[0][9][5] = 40.0
coordinates[1][9][5] = 0.0
coordinates[2][9][5] = 77.9037868142
coordinates[0][9][6] = 40.0
coordinates[1][9][6] = 3.75
coordinates[2][9][6] = 77.4386854227
coordinates[0][9][7] = 40.0
coordinates[1][9][7] = 7.5
coordinates[2][9][7] = 76.026311235
coordinates[0][9][8] = 40.0
coordinates[1][9][8] = 11.25
coordinates[2][9][8] = 73.6121593217
coordinates[0][9][9] = 40.0
coordinates[1][9][9] = 15.0
coordinates[2][9][9] = 70.0927956355
coordinates[0][9][10] = 40.0
coordinates[1][9][10] = 18.75
coordinates[2][9][10] = 65.2897388569
coordinates[0][10][0] = 50.0
coordinates[1][10][0] = -18.75
coordinates[2][10][0] = 60.1040764009
coordinates[0][10][1] = 50.0
coordinates[1][10][1] = -15.0
coordinates[2][10][1] = 65.2897388569
coordinates[0][10][2] = 50.0
coordinates[1][10][2] = -11.25
coordinates[2][10][2] = 69.0543264394
coordinates[0][10][3] = 50.0
coordinates[1][10][3] = -7.5
coordinates[2][10][3] = 71.622273072
coordinates[0][10][4] = 50.0
coordinates[1][10][4] = -3.75
coordinates[2][10][4] = 73.1197647699
coordinates[0][10][5] = 50.0
coordinates[1][10][5] = 0.0
coordinates[2][10][5] = 73.6121593217
coordinates[0][10][6] = 50.0
coordinates[1][10][6] = 3.75
coordinates[2][10][6] = 73.1197647699
coordinates[0][10][7] = 50.0
coordinates[1][10][7] = 7.5
coordinates[2][10][7] = 71.622273072
coordinates[0][10][8] = 50.0
coordinates[1][10][8] = 11.25
coordinates[2][10][8] = 69.0543264394
coordinates[0][10][9] = 50.0
coordinates[1][10][9] = 15.0
coordinates[2][10][9] = 65.2897388569
coordinates[0][10][10] = 50.0
coordinates[1][10][10] = 18.75
coordinates[2][10][10] = 60.1040764009

pointMatrixNew = NurbsMatrix.Matrix_Point3Dd(maxPoints,maxPoints)

for j in range(maxPoints):
	for k in range(maxPoints):
		pointMatrixNew.setelem(j,k,NurbsPoint.Point3Dd(coordinates[0][j][k],coordinates[1][j][k],coordinates[2][j][k]))


surface = NurbsSurface.NurbsSurfaced()
surface.globalInterp(pointMatrixNew,degree,degree)

def getPoint(u,v):
	tmpPoint = surface.pointAt(u,v)
	return numpy.array([tmpPoint.getx(), tmpPoint.gety(), tmpPoint.getz()])

def setPoint(point):
	return NurbsPoint.Point3Dd(point[0],point[1],point[2])

def distance(uvs):
	tmpSurface = getPoint(uvs[0],uvs[1])
	tmpLine = line(uvs[2])
	#return numpy.array([(tmpSurface[0]-tmpLine[0]),(tmpSurface[1]-tmpLine[1]),(tmpSurface[2]-tmpLine[2])])
	return (tmpSurface-tmpLine)


def line(s):
	aufPunkt = numpy.array([-25.24738656,11.27610049,78.91810196])
	sNormal = numpy.array([1,1,1])
	
	return aufPunkt+s*sNormal


def computeXY():
	tmp = scipy.optimize.broyden1(distance,[0.5,0.5,0.0],iter=20,alpha=0.010000000000000001,verbose=True)
	#tmp = scipy.optimize.broyden3(distance,[0.25,0.25,0.0],iter=100)
	#tmp = scipy.optimize.anderson(distance,[0.25,0.5,-0.4],iter=10, verbose=True)
	#tmp = scipy.optimize.anderson2(distance,[0.25,0.75,-0.4],iter=100)
	return tmp[:]

uValue = NurbsCurve.doublep()
vValue = NurbsCurve.doublep()

def distance2(s):
	minDistance = surface.minDist2(setPoint(line(s)),uValue,vValue)
	#print uValue.value(), vValue.value(), s
	return minDistance

def findS():
	tmp = scipy.optimize.fmin(distance2,1.0,retall=False,disp=False,full_output=False)
	return tmp[0]

## should converge to u=0.25, v=0.75 and s=-0.5
print getPoint(0.25,0.75)
print line(-0.5)
## should converge to u=0.25, v=0.75 and s=-0.5
print computeXY()

uValue.assign(0.0)
vValue.assign(0.0)
## should converge to u=0.25, v=0.75 and s=-0.5
print "line at s = ", findS()
print "End: ", uValue.value(), vValue.value()
