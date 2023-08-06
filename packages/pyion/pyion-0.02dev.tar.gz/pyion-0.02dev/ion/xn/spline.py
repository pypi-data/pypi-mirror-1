import math

def CRInterp(points, pos):
    """Catmull-Rom interpolation.
       Curve passes through the points exactly, with neighbouring points influencing curvature.
       points[] should be at least 3 points long."""

    #catmull-rom
    #
    # C++:
    #float t2 = t * t;
    #float t3 = t2 * t;
    #out.x = 0.5f * ( ( 2.0f * p1.x ) +
    #( -p0.x + p2.x ) * t +
    #( 2.0f * p0.x - 5.0f * p1.x + 4 * p2.x - p3.x ) * t2 +
    #( -p0.x + 3.0f * p1.x - 3.0f * p2.x + p3.x ) * t3 );
    #out.y = 0.5f * ( ( 2.0f * p1.y ) +
    #( -p0.y + p2.y ) * t +
    #( 2.0f * p0.y - 5.0f * p1.y + 4 * p2.y - p3.y ) * t2 +
    #( -p0.y + 3.0f * p1.y - 3.0f * p2.y + p3.y ) * t3 );
    
    # get the right slice of points
    #
    # four points, like so:
    #
    #     vv
    # 0  1  2  3
    # 
    # with pos being somewhere in the area marked with v
    #
    # Thus, while the number of input points should be >=4, only 3 of these may be used in 
    # some cases:
    #
    #  vv            vv
    # 0  1  2    1  2  3
    #
    # and the missing point then needs to be inserted next to the relevent segment:
    # 
    #     vv
    # 0  1  2  3 
    #
    # I use linear extrapolation to calculate the missing point here, the missing point is M:
    #
    # M = n0 - (n1 - n0)
    # 
    # n0 is the immediate neighbor of the missing point, n1 is the next closest neighbour
    #
    # (so, n0,n1 will correspond either to points 0,1 or points -1,-2)    
    #
    
    
    lbound = int(math.floor(pos) - 1)
    ubound = int(math.ceil (pos) + 1)
    t = pos % 1.0
    if abs ((lbound + 1) - pos) < 0.0001:
	# sitting on a datapoint, so just return that.
	return points[lbound+1]
#    print lbound,ubound
    if lbound < 0:
	p = points[:ubound+1]
#	print p
	# extend to the left linearly
	while len(p) < 4:
	    print '%r ->' % p
	    p.insert(0, p[0] - (p[1] - p[0]))
	    print p
    else:
	p = points[lbound:ubound+1]
	# extend to the right linearly
	while len(p) < 4:
	    print ':%r ->' % p
	    p.append(p[-1] - (p[-2] - p[-1]))
	    print p

    # currently has no handling of out-of-range positions (<0.0 or >(len(curve))
#    if len(p) < 4:
    t2 = t * t
    t3 = t2 * t
    tmp = 0.5 * ( (2 * p[1]) + (-p[0] + p[2]) * t + ((2 * p[0]) - ( 5 * p[1]) + (4 * p[2]) - p[3] ) * t2 +
          (-p[0] + ( 3 * p[1]) - ( 3 * p[2]) + p[3] ) * t3)
    return tmp

toomp = [0.0,1.0,4.0,8.0]
l = {}
for t in range(1,31):
    print t
    l[t/10.0] = CRInterp(toomp, t/10.0)

print 'CR:', l

class _Spline(list):
    __slots__ = ('factor', 'extend')
    def segment (self, seg):
	return self[seg * 4: (seg + 1) * 4]

    def getAt (self, x):
	"""Return (dims) values corresponding to the point x along the spline.
	One scaled unit of x corresponds to one spline segment.
	"""
	#determine segment
	x /= self.factor
	segment = math.floor (x / 1.0)
	nsegs = len(self) / 4
	if segment > nsegs or segment < 0:
	    # extension behaviour
	    if self.extend == 0: #crop (values past limits are assigned the closest endpoint value)
		return self.crop (segment)
	    elif self.extend == 1: # linear extension
		diff = self[-4] - self[-1]
		#values = 
	    elif self.extend == 2: # cumulative repeat
		pass
		# offset the segment appropriately so that it is continuous with the previous endpoint
	    else: # simple repeat
		segment = segment % nsegs
	

    # out-of-range handlers
    def crop (self, vseg):
	if vseg > 0:
	    return self[-1]
	else:
	    return self[0]

    def repeat (self, vseg):
	return segment (vseg % len(self))


    def __repr__ (self):
	return 'Spline (%s, %d, %d)' % (list.__repr__ (self), self.factor, self.extend)

class _Spline2D(_Spline):
	pass

def Spline (args, factor = 1, extend = 0):
    assert (len(args) % 4) == 0
    tmp = _Spline (args)
    tmp.extend = extend
    tmp.factor = factor
    return tmp
    

def spline (points, num_points):

	dt = 1.0 / (num_points - 1)
	dt2 = (dt * dt)
	dt3 = (dt2 * dt)

	xdt2_term = 3.0 * (points[2] - (2.0 * points[1] + points[0]))
	xdt3_term = points[3] + (3.0 * (-points[2] + points[1])) - points[0]

	xdt2_term = dt2 * xdt2_term
	xdt3_term = dt3 * xdt3_term

	dddx = 6.0 * xdt3_term
	ddx = -6.0 * xdt3_term + 2.0 * xdt2_term
	dx = xdt3_term - xdt2_term + 3.0 * dt * (points[1] - points[0])
	x = points[0]

	l = [ points[0] ]

	for i in xrange(1,num_points):
		ddx += dddx
		dx += ddx
		x += dx

		l.append(x)

	l[-1] = points[3]

	return l

# The below doesn't work because spline() is intended to always have a 4-long input.
# For longer inputs, they are divided into segments
#
# spline segment consists of A, B, C, D.
# 
# values start at A, leaving in the direction of B, moving then towards C so that we approach D
# from approximately the direction of C.
#

tmp = Spline(range(8))

print tmp
print tmp.segment(0)
print tmp.getAt(10101)

def dcGetO (points, t):
    """de Castelijau's algorithym, optimized for 4-point input.
       Find the value of a given point T in a cubic spline
       via simple subdivision.
       Further Optimized version (one liner)
       """    
    l = points   
    it = 1.0 - t
    l = (((l[0] * it) + (l[1] * t)), ((l[1] * it) + (l[2] * t)), ((l[2] * it) + (l[3] * t)))
    l = (((l[0] * it) + (l[1] * t)), ((l[1] * it) + (l[2] * t)))
    return (l[0] * it) + (l[1] * t)


def dcGet (points, t):
    """de Castelijau's algorithym, optimized for 4-point input.
       Find the value of a given point T in a cubic spline
       via simple subdivision.
       """       
    it = 1.0 - t
    l = points
    print l
    l = [((l[0] * it) + (l[1] * t)), ((l[1] * it) + (l[2] * t)), ((l[2] * it) + (l[3] * t))]
    print l
    l = [((l[0] * it) + (l[1] * t)), ((l[1] * it) + (l[2] * t))]
    print l
    return (((l[0] * it) + (l[1] * t)))

def quadraticToCubic (points):
    """Expand a quadratic curve segment:
    
         B
       .._..
       ./ \.
       |   |  
       +...+
       A   C
    
       This is actually extremely trivial - a quadratic curve ABC translates directly to the cubic
       curve ABBC -- ie you just duplicate the control point!
       
       This is a reference implementation, so I know what is going on. For a many-segmented curve
       you would probably implement an optimized expansion maybe using fancy slicing.

       Converting back cubic -> quadratic -- the nicest thing to do is probably to just average 
       BC so ABCD -> AvC where v is the average (may be more edifying to do the average in polar coords
       relative to the centre of the line AD.)
       
       note that in a cubic spline, each segment is actually quadratic
       
         C
       .._..
       ./ \.
       |   |  
       +...+    (A C and E are control points; 
       B   D     all of the points ABCDE contribute to the result,
      |    |     so the interpolation is cubic, each segment is quadratic.)
      |     \
      A      -
              \
	       E
	       
      and similarly for other order splines -- quintic spline == cubic segment
      
    """
    return points[0], points[1], points[1], points[2]

def xtest (a,b,c, max):
    """test, expands a 1d curve into 4 points"""
    # as b approaches max, ob approaches c and oc approaches a
    fac = min(1.0, b / max)
    ifac = 1.0 - fac
    return [a, (a * ifac) + (c * fac), (c * ifac) + (a * fac),c]

#138000 per second.
#import time
#tmp = time.time()
#i = 0
#while i < 1000000:
#    t = dcGetO ([0.0,1.0,2.0,3.0], i / 1000000.0)
#    i+= 1
#tmp2 = time.time()
#print tmp2 - tmp

tmp = [0.0, 0.25, 2.75,3.0]

print dcGetO (tmp, 0.5)
##
#print spline( (0.0, 1.0, 2.0, 3.0), 8)
for v in [int ((v/3.0)*80) for v in spline( tmp, 16)]:
    print max(1,v)*'*'

#s = spline( (0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0), 16)
#print(s)