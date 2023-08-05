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

import math
import NurbsCurveD
import NurbsPointD
import NurbsHPointD
#import NurbsVectorD
#import NurbsColor

# Printing Options
cp   = 1
magf = 1
dash = 2

radius = 100.0

curve=NurbsCurveD.NurbsCurve3Dd()
point=NurbsPointD.Point3Dd(0.0,0.0,0.0)
curve.makeCircle(point, radius, 0.0, 2.0*math.pi)
curve.writePS("curve01.ps",cp,magf,dash)

#red = NurbsColor.redColor
#curve.writeVRML97("curve97.wrl")
#curve.writeVRML97("curve97.wrl",0.5)

print curve.length()
print curve.length(0.000001,100)
print curve.lengthIn(0.0,1.0,0.000001,100)
print 2*math.pi*radius

