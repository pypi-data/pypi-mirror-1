""" Conclusion : for color interpolation, k=2 is more reliable than k = 3.
    K= 2 reduces extrapolation error (the amount of spline areas where
    some of the values N between two endpoints A and B do not conform
    to min(A,B) <= v <= max (A,B)

see Plots/LABInterp/blackbluegreenwhite-k2-vs-k3-L-A-B.svg
and it's -image companion (a visual comparison)

to make the image version:
splinify your color channels
convert RGB -> LAB 
interpolate
convert LAB -> RGB
reshape to (N, 1) (rather than (N, ))
numpy.tile ((97, 1,1))
numpy.clip (0,1.0)
{
subplot(I1#)
imshow(result)
}
for each image

for the base bar:
reshape (NCOLORS, 3) to (1,NCOLORS, 3)
result = scipy.ndimage.zoom(colors, (N, N/NCOLORS, 1), order = 0)

note -- use InterpolatedUnivariateSpline rather than UnivariateSpline;
then you needn't specify s=0

"""

# btw, use operator.isMappingType() instead of type(x) == dict

# calculate a curve between p2 + p3, accounting for p1 and p4 if existing
# ganked from gimp/app/core/gimpcurve.c
#
# pX are indices into curve
# was gimp_curve_plot
def plot (curve, p1, p2, p3, p4):
    #gint    i;
    #gdouble x0, x3;
    #gdouble y0, y1, y2, y3;
    #gdouble dx, dy;
    #gdouble y, t;
    #gdouble slope;

    # the outer control points for the bezier curve. 
    x0 = curve.points[p2][0];
    y0 = curve.points[p2][1];
    x3 = curve.points[p3][0];
    y3 = curve.points[p3][1];

    #
    # the x values of the inner control points are fixed at
    #  x1 = 1/3*x0 + 2/3*x3   and  x2 = 2/3*x0 + 1/3*x3
    # this ensures that the x values increase linearily with the
    # parameter t and enables us to skip the calculation of the x
    # values altogehter - just calculate y(t) evenly spaced.
    #

    dx = x3 - x0;
    dy = y3 - y0;

    if not (dx > 0): return

    if p1 == p2 and p3 == p4:
        # No information about the neighbors,
        # calculate y1 and y2 to get a straight line
        y1 = y0 + dy / 3.0
        y2 = y0 + dy * 2.0 / 3.0
    elif (p1 == p2 and p3 != p4):
        # only the right neighbor is available. Make the tangent at the
        # right endpoint parallel to the line between the left endpoint
        # and the right neighbor. Then point the tangent at the left towards
        # the control handle of the right tangent, to ensure that the curve
        # does not have an inflection point.
        #
        slope = (curve.points[p4][1] - y0) / (curve.points[p4][0] - x0)

        y2 = y3 - slope * dx / 3.0;
        y1 = y0 + (y2 - y0) / 2.0;
    elif p1 != p2 and  p3 == p4:
        # /* see previous case */
        slope = (y3 - curve.points[p1][1]) / (x3 - curve.points[p1][0]);

        y1 = y0 + slope * dx / 3.0;
        y2 = y3 + (y1 - y3) / 2.0;
    else: # (p1 != p2 && p3 != p4) 
        # Both neighbors are available. Make the tangents at the endpoints
        # parallel to the line between the opposite endpoint and the adjacent
        # neighbor.
        #
        slope = (y3 - curve.points[p1][1]) / (x3 - curve.points[p1][0]);
        y1 = y0 + slope * dx / 3.0;
        slope = (curve.points[p4][1] - y0) / (curve.points[p4][0] - x0);
        y2 = y3 - slope * dx / 3.0;
        
    #
    # finally calculate the y(t) values for the given bezier values. We can
    # use homogenously distributed values for t, since x(t) increases linearily.
    #
    for i in range(int(dx+1)):
        t = i / dx;
        y = y0 * (1-t) * (1-t) * (1-t) +\
            3 * y1 * (1-t) * (1-t) * t +\
            3 * y2 * (1-t) * t     * t +\
            y3 * t     * t     * t;

        curve.curve[round(x0) + i] = min (255, max(0, round (y)));
    

class TestCurve (object):
    def __init__ (self, points, curve):
        self.points = points
        self.curve = curve

import numpy
import scipy.interpolate as si
pts = numpy.array([[0.,0.], [12., 4.], [16.,16.]])
cv = numpy.zeros (17)
c = TestCurve (pts, cv)
plot (c, 0, 0, 1, 2);
plot (c, 0, 1, 2, 2);
#print [int(v) for v in c.curve]
#print c.curve[12]


#def xpoints (startpt, endpt):
    

# insert points at start (cos(x), sin(y)), and end
spline = si.InterpolatedUnivariateSpline ([-12, 0, 12, 16], [-4, 0, 4, 16], k = 3)
#print spline (range(16+1)).astype('i4')

#Now, what I really want is to synthesize the points and interpolate from a UnivariateSpline.

def _tile (x, y, direction, roi):
    # tile 123123123
    imin, imax = None, None
    if direction == 1:
        # align by left edge, extending on right side
        xoffset = (roi[0] - x[0]) - 1 
#       yoffset = y[-1]
    else:
        # align by right edge, extending on left side
        xoffset = roi[-1] - x[-1] # top 3

    for i,v in enumerate(x):
        if v + xoffset == roi[0]:
            imin = i
        elif v + xoffset == roi[-1]:
            imax = i
    if direction == 1:       
        imin = (imin if imin else None)
        imax = (imax + 1 if imax else None)
        yimin = None
        yimax = imax - imin
    else:
        imin = (imin  if imin else None)
        imax = (imax + 1 if imax else None)
        yimax = None
        yimin = - (imax - imin)

#    print imin, imax
    newy = y[yimin:yimax]
#        yoffset = y
    newx = [v + xoffset for v in x[imin:imax]]
    if direction == 1:
        return x + newx, y + newy
    else:
        return newx + x, newy + y

def _angulartile (x, y, direction, roi):
    # tile like this:
    #
    #
    # 123456789
    pass
    

def _extend (x,y, direction, roi):
    """ extendCurve callback.

        For transposed x points that fall inside the ROI, 
        y matches the extrapolated value.
        """
    rx = []
    ry = []
    xtop = x[-1]
    xbot = x[0]
    if direction == 1:
        # align by left edge, extending on right side
        xoffset = xbot - roi[0]
        yoffset = y[-1]
    else:
        # align by right edge, extending on left side
        xoffset = xbot - roi[-1] # top 3
        yoffset = None # FILL IN LATER

def extendCurve (x, y, xrange, mode = 'extend'):
    """ Extend the points given so that the spline covers the specified range.

    The default mode, 'extend', simply samples outside the spline, and adds the results to the ends.  """
    pass


# XXXX troublesome -- replace it with a simple querier:
#
# inRange (x, y, k = 3)
# returns a list of segments, in (x,y) format, that have out of range midpoints (that is,
# not lo <= mid <= hi)
# or where min(y) <= v <= max(y) is not satisfied
# 
def expandCurve (x, y, k = 3, protected = (), threshold = 0):
    """Recursively subdivide the spline points in order to 
       guarantee 'reasonably-sensible' behaviour -- when interpolating in a segment
       A.. B, ensure that any sample taken inside that range falls between A's value and B's value.
       Low-order spline interpolation is used to fill in points where possible; when not possible,
       linear interpolation is used.

       For parts where violent behaviour is permissible, you can mark protected places
       ((x,x2),(x,x2),..)

       Returns an altered copy of x and y
       """
    # copy the data
    x = list (x)
    import os
    y = list (y)
    spl = si.InterpolatedUnivariateSpline (x, y, s = 0)
    xspl = si.InterpolatedUnivariateSpline (range(len(x)), x, k = 1, s = 0)
    # list of midpoint positions
    samplepos = xspl (numpy.arange(.5,len(x), 1.))
    sample = spl (samplepos)
#    print samplepos
    os.system('echo "BF %r, %r" >> /tmp/lickme' % (type(x), type(protected)))
    toadd = []
    for i in range (len (x)-1):
#        print 'x[i]',x[i]
	os.system('echo "AF %r, %r" >> /tmp/lickme' % ( type(x[i]), type(protected)))
        if int(x[i]) in protected:
            continue
        low = min (y[i], y[i+1])
        hi = max (y[i], y[i+1])
        # sanity check
        if low <= sample[i] <= hi:
            continue
	if abs (low - sample[i]) <= threshold:
	    continue
	if abs (hi - sample[i]) <= threshold:
	    continue
        derivs = spl.derivatives (samplepos[i])
#        print 'expanding %d-%d' % (x[i], x[i+1])
#        print low, hi, derivs
        derivs = derivs[(derivs >= low) & (derivs <= hi)]
        if len(derivs) == 0:
            # linear interpolation, if no more interesting value is guessable.
            derivs = [(y[i] + y[i+1]) / 2.0]
        toadd.append ((samplepos[i], derivs[0]))

#    x = x.tolist()
#    y = y.tolist()
    for pos, val in toadd:
        for i in range (len(x) - 1):
            low = min (x[i], x[i+1])
            hi = max (x[i], x[i+1])
            if low < pos < hi:
                x.insert(i+1, pos)
                y.insert(i+1, val)
                break
    
    if len(toadd) > 1: # just added some points?
        del spl
        del xspl
        del samplepos
        del sample
        # try another go.. until there are no more points to add
        x,y = expandCurve (x, y, k, protected)
    return x,y

def curveForOrder (x, y, range, k = 3, workk = -1):
    """ Add points to a curve so that there are enough to interpolate with the given order.

    """
    if workk < 1:
	workk = k
    workk = min (3, workk)
    if len(x) in (1, 2):
        # conic or cubic spline with x[0],y[0] (+x[1], y[1]?) as center point(s).
        x.insert (0, range[0][0])
        y.insert (0, range[1][0])
        x.append (range[0][1])
        y.append (range[1][1])
    while (len(x) < (k + 1)):
	# given a curve
	# 
	# ABCDEF
	#
	# pick any of the points
	#  .B.C.D.E.
	# 
	# sample from the conic curve (prevpoint, point, nextpoint)
	# XXX spline based x subdiv, too?
	#import random
	#slot = random.randint (1, len(x) - 1)
	y2 = numpy.asarray (y)
	tmp = numpy.abs (numpy.diff (y2))
	maxv = tmp.max()
	slot = tmp.tolist().index(maxv) + 1
#	print 'ABS' ,slot
#	slot = slot.index (maxv) + 1
	print ('subdividing at %d (diff %d)' % (slot, maxv))
	pointsy = [y[slot - 1], y[slot], y[slot], y[min(len(x) - 1, slot + 1)]]
	spl = si.InterpolatedUnivariateSpline ([0,1,2,3], pointsy, k = workk, s = 0)
	sample = spl([.5])[0]
	newx = si.InterpolatedUnivariateSpline ([0,1,2,3], [x[slot - 1], x[slot], x[slot], x[min(len(x) -1, slot + 1)]], k = workk, s = 0)([.5])[0] 
	#newx = (x[slot - 1] + x[slot]) / 2
	x.insert (slot, newx)
	y.insert (slot, sample)
    return x,y
    

#sampledat = numpy.arange (0.,5.001, 1/4.)
#print sampledat
#x,y = (range(6), [0,4,8,16, -256, 0])
#spl = si.UnivariateSpline (x, y, k = 3, s = 0.0)
#print 'prefilter', spl (sampledat).astype('i4')

#x,y = expandCurve (x, y, protected = (4.,))
#print x,y
#spl = si.UnivariateSpline (x, y, k = 3, s = 0.0)
#print spl (sampledat).astype('i4')

#x = [16]
#y = [32]
#x2,y2 = curveForOrder (list(x), list(y), ((0, 32), (0, -32)),k = 3, workk = 1)
#print '1.3', x2,y2
#print '2.5', curveForOrder (list (x), list (y), ((0, 32), (0, -32)),k = 5, workk = 2)
#print '1.5', curveForOrder (list (x), list (y), ((0, 32), (0, -32)),k = 5, workk = 1)
#spl = si.UnivariateSpline (x2, y2, k = 3, s = 0)
#print spl(range(32)).round().astype('i4')



def sample (spl, x, mode = 'tile'):
    minx = spl._data[0][0]
    maxx = spl._data[0][-1] + (spl._data[0][-1] - spl._data[0][-2])
    if mode == 'tile':
	t1 = x - minx
	t2 = t1 % (maxx - minx)
	t3 = t2 + minx
#	print t1,t2,t3
#	t3 = x % maxx
	print t3
        return spl(t3)
#    elif mode == 'extend'

def subdivide (x, y, k = 3):
    """
    1,2  4,8 ->
    1,2  2,5  4,8 (nonlinear)
    """
    ninputs = len(x)
    inputrange = range(ninputs)
    xspl = si.InterpolatedUnivariateSpline (inputrange, x, s = 0, k = k)
    yspl = si.InterpolatedUnivariateSpline (inputrange, y, s = 0, k = k)
    samprange = numpy.arange (0, ninputs, .5)
    return xspl (samprange), yspl (samprange)

def gimpSubdivide (vectors):
    """subdivide all strokes belonging to a vectors object."""
    for strokeid in vectors.strokes:
	t, npts, pts, closed = vectors.stroke_get_points (strokeid)
	#CACCACCACCA.. where C are control points (do not want!)
	x = pts[2::6]
	y = pts[3::6]
	nanchors = len(x)
	x,y = subdivide (x, y)
	arr = numpy.empty (shape = ((nanchors + nanchors - 1) * 3 * 2))
	arr[0::6] = x # control
	arr[1::6] = y # control
	arr[2::6] = x # anchor
	arr[3::6] = y # anchor
	arr[4::6] = x # control
	arr[5::6] = y # control
	arr = arr.tolist()
	newstrokeid = vectors.new_stroke_from_points (type, len(arr), arr, closed)
	vectors.remove_stroke (strokeid)

class multiSpline(object):
    def __init__ (self, x, y, k = 3, s = 0, subdiv = False, protected = ()):
	y= numpy.asarray (y)
	if y.ndim != 2:
	    raise ValueError ('multiSpline requires y.shape == (len (x), N) where N is the number of splines')
	if subdiv == True:
	    self._splines = []
	    for i in range(y.shape[-1]):
		thisx, thisy = expandCurve (x, y[:, i], k=k, protected = protected, threshold = .1)
		self._splines.append (si.InterpolatedUnivariateSpline(thisx, thisy, k=k, s=s))
	else:
	    self._splines = [si.InterpolatedUnivariateSpline(x, y[:, i], k=k, s=s) for i in range (y.shape[-1])]
    def __call__ (self, x):
	result = [s(x) for s in self._splines]
	for samples in result:
	    samples.shape = (samples.shape[0], 1)
	result = numpy.hstack (result)
	return result

#class stackedspline
#
# -> used for things like gradient mapping.
# You have 3 splines, one each for RGB, and the result is returned in this RGB format:
#
# [[[R,G,B],[R,G,B]],[[R,G,B],[R,G,B]]]
