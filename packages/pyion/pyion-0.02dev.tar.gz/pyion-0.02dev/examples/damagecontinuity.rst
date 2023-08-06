#!/usr/bin/python
from ion.maths.damagecontinuity2 import totaldmg, adjustvsArmor
from numpy import arange
import numpy
import sys
minx, maxx = 0.09, 0.9901
miny, maxy = 0, 100.01

scale = 144.0 # points
iterations = 96
xv, yv, data, color= [],[],[],[]
for x in arange(minx, maxx, 0.05):
    sys.stdout.write ('-'); sys.stdout.flush()
    for y in arange (miny, maxy, 5):
#        xv.append (x)
#        yv.append (y)
	sum = 0.0
	minv = 9000000
	maxv = -9000000
	for i in range(iterations):
	    tmp = totaldmg(x,y)
	    sum += tmp
	    minv = min (tmp, minv)
	    maxv = max (tmp, maxv)
	xv.append (x)
    	yv.append (y)
        data.append (maxv)
	color.append ('y')
	xv.append(x)
	yv.append(y)
	data.append (minv)
	color.append ('b')
	sys.stdout.write ('|'); sys.stdout.flush()
import pylab
maxdata = max(data)
factor = scale / maxdata
import math
data = [(math.sqrt(v) + v) / 4.0 for v in data]
#data = [v * factor for v in data]

pylab.scatter (xv, yv, data, color = color, marker = 'o', linewidth = 0.0, alpha = .5)
pylab.title ('max data value : %.2f' % maxdata)
pylab.show()